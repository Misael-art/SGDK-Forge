# Concepcao de cena — `branding_sequence_v2` "A FORJA"

Companheiro de `doc/branding_sequence_contract.json` e `doc/branding_v2_art_direction.md`.
Contrato machine-readable: `doc/branding_v2_cinematic_storyboard.json`.

Este documento existe porque **assets nao sao cena**. O contrato dizia quais tecnicas e quais
arquivos; nao dizia o que se move, para onde, em quanto tempo e com que peso. Sem isso a lista
de assets estava incompleta — e estava mesmo: a coreografia adiciona um asset e mais quadros a
dois outros. Ver a secao final.

---

## O que faz isto ser cena e nao slideshow

Tres regras estruturais, e todas sao verificaveis:

**1. Tomada continua.** Zero `VDP_clearPlane` entre atos. A camera nunca corta. Cada transicao
e feita por luz, scroll ou paleta. O v1 tinha tres cortes a preto e por isso lia como tres
cartoes, nao como uma abertura.

**2. Escalada de hardware.** Cada ato liga uma camada nova: ato 1 estabelece luz (H-Int +
Shadow/Highlight mascarado), ato 2 acrescenta populacao de sprites e varredura especular, ato
3 acrescenta scroll por coluna. Quem assiste sente o sistema crescendo, mesmo sem saber o
nome de nada.

**3. Consequencia fisica em todo efeito.** Nada de FX decorativo: o martelo bate e a tela
treme; a brasa cai e acende o que passa perto; o metal esquenta e o ar acima dele ondula. Essa
e a regra maximalista do workspace aplicada a uma cena sem gameplay.

**Momento de assinatura:** F120. O martelo encosta na bigorna, a tela pisca em branco por 2
quadros, treme, e do impacto saem 32 estilhacos que **voltam** e se montam no logo. A marca
nao aparece: ela e forjada na frente de quem assiste. Se so um segundo desta abertura for
lembrado, e esse.

---

## ATO I — IGNITION (F0-120, 2 segundos)

### F0-F8 — a forja ja esta viva antes de voce ver

Tela praticamente preta. **Nada se move a nao ser a paleta.** `PAL0[9..12]` gira em CRAM a um
passo a cada 8 quadros (7,5 Hz), entao a unica coisa viva e o brilho de brasa pulsando nas
linhas de baixo, entregue pelas bandas de H-Int.

Isto e proposital: comeca com a maquina respirando, nao com um logo.

### F8-F96 — a queda da brasa

A brasa cai em parabola do alto a direita ate a face da bigorna.

| Parametro | Valor |
|---|---|
| origem | x=232, y=-16 (fora da tela) |
| destino | x=128, y=104 (face da bigorna) |
| duracao | 88 quadros |
| horizontal | velocidade constante com leve arrasto, `fix16` |
| vertical | aceleracao constante, `v += g` por quadro |
| rastro | 5 fantasmas nas posicoes de t-2, t-4, t-6, t-8, t-10 |

A aceleracao e o que da **peso**. Velocidade constante leria como um adesivo deslizando.

**Sprites vivos: 6** (1 brasa + 5 fantasmas). Os fantasmas usam a rampa mais fraca de
`PAL3[10..13]`, entao o rastro apaga por cor, nao por transparencia — que o VDP nao tem.

**Luz mascarada:** enquanto a brasa desce, o runtime liga o bit de highlight numa janela de
tiles que a segue em BG_A. Os tiles da bigorna e da parede proximos acendem na passagem e
apagam depois. E isto que separa "luz dinamica" de "luz pintada no fundo": a fonte se move e o
cenario responde.

### F96-F120 — antecipacao

O martelo entra pelo alto a direita e **sobe**, carregando o golpe. A brasa, ja pousada na
bigorna, pulsa por CRAM.

Antecipacao e o que faz o impacto valer. Sem esses 24 quadros de recuo, F120 vira um flash
sem causa.

---

## ATO II — STRIKE (F120-300, 3 segundos)

### F120 — o impacto

Quatro coisas no mesmo quadro:

1. **Flash de CRAM** por 2 quadros, branco, escrito com mascara de linhas para nao gerar CRAM
   dots;
2. **Hit de DAC** — o unico PCM da abertura, guardado para este instante;
3. **Screen shake**: deslocamento vertical de 3px nos dois planos, decaindo para 0 em 6
   quadros (3, 2, 2, 1, 1, 0). Barato e le como massa;
4. **32 estilhacos nascem** no ponto de contato.

### F122-F180 — o enxame que monta a marca

Esta e a tese da abertura, e ela tem tres tempos:

| Fase | Quadros | O que acontece |
|---|---|---|
| explosao | F122-F140 | os 32 estilhacos saem em leque radial, com velocidades diferentes |
| suspensao | F140-F150 | desaceleram quase ate parar, girando |
| convergencia | F150-F180 | cada um e puxado para um ponto da silhueta do logo, com ease-in |

Cada estilhaco carrega um destino fixo: um ponto sobre a forma das letras. Na convergencia o
runtime interpola posicao atual -> destino. Nos ultimos quadros a leitura vira "as letras estao
se fechando".

**Pressao de scanline:** os 32 convergem para uma faixa de 64px de altura. O pior quadro
precisa ficar abaixo de 20 sprites por linha — e por isso a convergencia e escalonada, com os
estilhacos chegando em ondas de cima para baixo em vez de todos juntos. **Claim exige
`vdp_scanline_simulator.py`, nao estimativa.**

### F180 — a troca

Os estilhacos somem e o logo em tilemap assume o lugar exato onde eles pousaram. Um quadro. Se
a arte estiver alinhada, o olho nao ve a troca: ve o metal solidificando.

Depois disso o orcamento de sprites volta a **zero** e o resto do ato roda sem custo de SAT.

### F180-F300 — a varredura especular e o ar quente

**Varredura:** uma coluna de highlight de 24px de largura atravessa o logo da esquerda para a
direita a 3px por quadro, cruzando os 224px em ~80 quadros. Nao e brilho pintado andando: o
runtime liga o bit de highlight nos tiles sob a coluna. **Por isso o wordmark precisa do degrau
de luz em `PAL1[13..14]`** — sem ele o operador nao tem para onde clarear e a varredura nao
existe.

**Ar quente:** as 48 scanlines de baixo recebem deslocamento horizontal por linha, com
amplitude caindo de 6px para 1px ao longo do ato. Tabela enviada por DMA no VBlank, 448 bytes
por quadro. E a consequencia fisica do calor: o ar acima da forja distorce o que esta atras.

---

## ATO III — SIGNATURE (F300-520, 3,7 segundos)

### F300-F360 — a cortina por coluna

O cenario da forja se abre em colunas verticais que sobem. Com `VSCROLL_2TILE` sao 20 colunas
controlaveis em 320px. As colunas sobem com **offsets escalonados**, nao uniformes: as do
centro primeiro, as das bordas depois. Uniforme leria como um slide; escalonado le como uma
cortina.

Por tras delas ja esta o wordmark do autor em BG_A.

### F360-F430 — autor

O wordmark do autor fica exposto, com uma passagem lenta de highlight — mais devagar que a do
ato 2, porque aqui o tempo e de respiro, nao de impacto.

### F430-F480 — projeto

O wordmark do projeto assume o centro. O do autor sai por scroll vertical para cima.

### F480-F510 — presents

O wordmark `presents` entra por baixo, pequeno, sem chanfro. Ele nao compete: entra, respira,
para.

### F510-F520 — entrega

Fade de paleta para a cena seguinte. **Sem corte a preto**, sem `VDP_clearPlane`. A ultima
coisa que some e a rampa de brasa, fechando o circulo com o F0.

---

## Orcamento ao longo do tempo

| Ato | Sprites (pico) | DMA por quadro | H-Int | Notas |
|---|---|---|---|---|
| I | 6 | nenhum | 7 bandas de paleta | brasa + 5 fantasmas |
| II F120-180 | **33** | nenhum | banda de varredura | 32 estilhacos + martelo |
| II F180-300 | 0 | 448 B (tabela HScroll) | banda de varredura | logo em tilemap |
| III | 0 | tabela de coluna | nenhum | cortina por scroll |

O pico e F150-F180. Tudo depois disso e barato — a abertura gasta o orcamento no momento de
assinatura e devolve.

`measurement_level: estimated`. Nenhum destes numeros vale como aprovacao: exigem
`res_graph_report.json`, `sprite_scanline_pressure_report` do simulador e `visual_vdp_dump.bin`.

---

## O QUE ISTO MUDA NA LISTA DE ASSETS

A coreografia invalidou parte do contrato de assets. Tres correcoes:

### 1. O martelo tem que virar sprite — asset NOVO

O contrato colocava o martelo dentro de `img_forge_bg_a_props`, uma imagem estatica. **Mas o
martelo sobe em F96-F120 e bate em F120.** Imagem estatica nao bate.

- **remover** o martelo de `img_forge_bg_a_props`;
- **criar `spr_forge_hammer`**: strip de 6 quadros — repouso, recuo, dois intermediarios de
  descida, contato, retorno. Tamanho alvo 48x48 (6x6 tiles).
- consequencia de orcamento: 6 quadros de 36 tiles = 216 tiles residentes. E muito. Decidir
  entre reduzir para 4 quadros, diminuir para 40x40, ou fazer streaming da janela de animacao.
  **Essa decisao precisa do `res_graph_report` antes da arte comecar.**

### 2. A brasa precisa de quadros de impacto

O contrato pedia 4 quadros de rotacao. A coreografia tem a brasa **pousando** na bigorna em
F96. Sem quadro de impacto ela para no ar.

- `spr_forge_ember`: de 4 para **6 quadros** — 4 de rotacao em queda, 1 de esmagamento no
  contato, 1 de assentamento.

### 3. O fundo precisa ser desenhado sabendo do ar quente

`img_forge_bg_b` recebe deslocamento por linha nas 48 scanlines de baixo. Detalhe critico,
texto ou aresta fina nessa faixa **quebra** quando cisalhada.

- a faixa inferior de 48px precisa ser composta de material continuo — brasa, piso, fumaca —
  sem elemento que dependa de alinhamento horizontal exato.

### Contagem revisada

De **8** para **9** assets, com dois ganhando quadros:

| # | Asset | Mudanca |
|---|---|---|
| 1 | `img_forge_bg_b` | faixa inferior de 48px pensada para cisalhamento |
| 2 | `img_forge_bg_a_props` | **martelo removido** |
| 3 | `spr_forge_hammer` | **NOVO**, 6 quadros, pendente de decisao de orcamento |
| 4 | `spr_forge_ember` | 4 -> **6 quadros** |
| 5 | `spr_forge_shard` | sem mudanca |
| 6 | `img_logo_engine_v2` | **degrau de luz em PAL1[13..14]** obrigatorio |
| 7 | `img_logo_author_v2` | sem mudanca |
| 8 | `img_logo_project_v2` | sem mudanca |
| 9 | `img_presents_text_v2` | sem mudanca |

---

## Pendencia antes de liberar os assets

O `spr_forge_hammer` a 6 quadros de 48x48 pesa 216 tiles residentes. Antes de mandar autorar,
alguem precisa decidir entre reduzir quadros, reduzir tamanho ou fazer streaming — e essa
decisao muda o que o agente de arte desenha. **Nao e decisao de arte, e de orcamento**, e ela
deveria sair de um `res_graph_report` real em vez de estimativa.
