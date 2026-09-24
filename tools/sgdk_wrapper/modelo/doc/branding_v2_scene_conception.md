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

**Vitrine:** a abertura declara 31 tecnicas do registry canonico, das quais 18 carregam claim
de compreensao e 13 sao disciplina de habilitacao. Nove foram rejeitadas com motivo escrito —
inclusive coisas que pareceriam impressionantes (boss por plane takeover, cinematica articulada,
escala pseudo-3D) e que nesta cena seriam espetaculo sem consequencia. A vitrine nao e a
contagem: e o fato de cada item ter que dizer o que o espectador entende, e o que se perderia
sem ele.

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

Cinco coisas no mesmo quadro:

1. **Flash de CRAM** por 2 quadros, branco, escrito com mascara de linhas para nao gerar CRAM
   dots;
2. **Hit de DAC** — o unico PCM da abertura, guardado para este instante;
3. **Screen shake**: deslocamento vertical de 3px nos dois planos, decaindo para 0 em 6
   quadros (3, 2, 2, 1, 1, 0). Barato e le como massa;
4. **56 estilhacos nascem** no ponto de contato, 2 por quadro;
5. **a bigorna fica marcada** — o golpe grava uma cicatriz incandescente na face, escrita em
   tiles, que **permanece ate o fim da abertura**. E a unica coisa da cena que sobrevive ao
   proprio beat que a criou.

### F122-F180 — o enxame que monta a marca

Esta e a tese da abertura, e ela tem tres tempos:

| Fase | Quadros | O que acontece |
|---|---|---|
| nascimento | F122-F138 | os estilhacos surgem **2 por quadro**, nunca todos de uma vez |
| explosao | ate F150 | cada um sai em leque radial, com velocidade propria |
| convergencia | F152-F194 | puxados para pontos da silhueta, escalonados **5 quadros por fileira** |
| pouso | continuo | cada estilhaco que chega vira tile e **sai do SAT**; o ultimo pousa em F194 |

Os tres parametros acima nao sao gosto: sao o resultado de medicao. Ver a secao de orcamento.

Cada estilhaco carrega um destino fixo: um ponto sobre a forma das letras. Na convergencia o
runtime interpola posicao atual -> destino. Nos ultimos quadros a leitura vira "as letras estao
se fechando".

**Pressao de scanline:** os 32 convergem para uma faixa de 64px de altura. O pior quadro
precisa ficar abaixo de 20 sprites por linha — e por isso a convergencia e escalonada, com os
estilhacos chegando em ondas de cima para baixo em vez de todos juntos. **Claim exige
`vdp_scanline_simulator.py`, nao estimativa.**

### F180-F194 — o pouso progressivo

Nao existe um quadro de troca. **Cada estilhaco que chega ao alvo vira tile do logo e sai do
SAT na hora.** O logo se constroi peca por peca e a populacao de sprites **cai** durante a
montagem, em vez de picar no fim.

Isso comecou como correcao de orcamento e virou a melhor decisao narrativa do ato: o olho ve
o metal solidificando pedaco a pedaco, nao um passe de magica.

Depois de F194 o custo de SAT e **zero** e o resto do ato roda de graca.

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

| Ato | Sprites totais | Pico por scanline | DMA por quadro | Notas |
|---|---|---|---|---|
| I | 6 | 2 | 203 B medios (streaming do martelo) | brasa + 5 fantasmas |
| II F120-194 | 33 | **15 medido** | 1152 B no pico de troca | estilhacos + martelo |
| II F194-300 | 0 | 0 | 448 B (tabela HScroll) | logo em tilemap |
| III | 0 | 0 | tabela de coluna | cortina por scroll |

### A pressao de scanline foi medida, nao estimada

A primeira coreografia que escrevi **quebrava o hardware**. Rodada no
`vdp_scanline_simulator.py` canonico, media **36 sprites numa scanline** contra o limite de
20, com `status: error`. A estimativa que eu tinha escrito no contrato dizia 12.

O que estava errado: todos os 32 estilhacos nasciam no mesmo ponto no mesmo quadro, entao
F122-F124 era uma pilha. E a convergencia terminava com todos empacotados na faixa de 64px do
logo, o que dava 24 em F179.

Tres correcoes, medidas ate passar com folga:

1. **spawn escalonado** — 2 estilhacos por quadro, ao longo de 16 quadros;
2. **pouso progressivo** — cada estilhaco que chega sai do SAT, entao a populacao cai durante
   a montagem em vez de picar no fim;
3. **recuo rapido do martelo** — 10 quadros em vez de ficar em cena ate F150. Foi a correcao
   de maior efeito: o martelo tem 4 sprites de hardware e coexistia com a nuvem.

Resultado medido pela ferramenta canonica: **15 sprites por scanline, margem de 25%**.

`measurement_level: measured_by_simulator` para a pressao de scanline. O restante segue
`estimated` e exige `res_graph_report.json` e `visual_vdp_dump.bin`.

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

## Orcamento do martelo: RESOLVIDO por streaming

Decisao do curador em 2026-08-17: **streaming**, porque a premissa do projeto e maxima
qualidade visual e o golpe e o momento de assinatura da abertura.

| | Sem streaming | Com streaming |
|---|---|---|
| tiles residentes | 216 | **72** (janela dupla) |
| bytes residentes | 6912 | 2304 |
| custo por troca de quadro | 0 | 1152 B |
| custo medio por quadro | 0 | 203 B |

Economia de **144 tiles** de VRAM, preservando os 6 quadros a 48x48. O swing dura 34 quadros
para 6 quadros de arte, entao a troca acontece a cada 5,7 quadros — nao a cada quadro.

Pior coincidencia teorica: 1600 B num VBlank (troca de quadro somada a tabela de HScroll). As
duas janelas quase nao se sobrepoem, entao isso e teto e nao expectativa. Contrato completo em
`doc/branding_v2_dma_queue_contract.json`, com ordem de recuo declarada caso o envelope medido
nao comporte — e cortar quadro de arte e o **ultimo** recurso, porque contraria a premissa da
decisao.
