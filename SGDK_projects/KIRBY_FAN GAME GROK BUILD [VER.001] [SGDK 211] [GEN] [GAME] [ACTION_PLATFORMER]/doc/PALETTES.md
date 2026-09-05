# PALETTES.md — Contrato de Cor

> **Dono unico:** `systems/raster.c` para CRAM em runtime. Nenhum outro sistema
> escreve cor. Ver [ARCHITECTURE.md](ARCHITECTURE.md) §6.1.
> **Status:** `documentado`. Nada aqui foi visto rodando em ROM.
> Marcas: `[VERIFICADO]` tem citacao de header. `[DECIDIDO]` e escolha de projeto.
> `[NAO MEDIDO]` bloqueia claim de pronto.

---

## 1. O formato de cor do VDP `[VERIFICADO]`

De `sdk/sgdk-2.11/inc/pal.h:18-26`:

```
VDPPALETTE_REDSFT    1      VDPPALETTE_REDMASK    0x000E
VDPPALETTE_GREENSFT  5      VDPPALETTE_GREENMASK  0x00E0
VDPPALETTE_BLUESFT   9      VDPPALETTE_BLUEMASK   0x0E00
                            VDPPALETTE_COLORMASK  0x0EEE
```

Uma entrada de CRAM e uma word de 16 bits com este layout:

```
bit  15 14 13 12 | 11 10  9  8 |  7  6  5  4 |  3  2  1  0
      0  0  0  0 |  B  B  B  0 |  G  G  G  0 |  R  R  R  0
```

**Teste de legalidade, e este e exatamente o gate:**

```
(word & ~0x0EEE) == 0
```

Ou seja: bits 0, 4, 8 e 12-15 **precisam ser zero**. `gates.py` ja implementa
isso com `mask: '0x0EEE'` — confere com o header.

Macro canonica para construir cor: `RGB3_3_3_TO_VDPCOLOR(r, g, b)` com r/g/b em
0-7 (`pal.h:48`). Nao construa word de cor a mao.

### 1.1 A grade de 8 valores por canal

3 bits = 8 niveis. Convertidos para 8 bits (`round(n * 255 / 7)`):

| nivel | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| 8-bit | 0 | 36 | 73 | 109 | 146 | 182 | 219 | 255 |

**512 cores possiveis no total. 64 na tela.** Toda arte deste projeto ja foi
validada contra essa grade: 11 de 11 entregaveis a 0.00% de pixels ilegais.

### 1.2 Formula canonica de luminancia `[DECIDIDO]`

Canonizada no loop de arte (ver `doc/art/R2_VERDICT_AND_R3_PACK.md` §5.1), porque
diretor e executor estavam usando formulas diferentes e chegando a numeros
diferentes para a mesma imagem:

```
L = (0.2126*R + 0.7152*G + 0.0722*B) / 255      com R,G,B em 0-255
```

Perceptualmente correta para sRGB. **Toda metrica de valor neste projeto usa
esta formula.** Criterio de valor que nao cita a formula e criterio invalido.

### 1.3 Como quantizar uma imagem qualquer

Ordem obrigatoria. Inverter os passos 2 e 3 e o erro classico:

1. **Reduzir a contagem de cores primeiro**, na resolucao de trabalho, com
   objetivo de paleta (15 cores por bloco de 16).
2. **Depois** snap de cada canal para o vizinho mais proximo na grade de 8.
3. **Nunca** snap antes de reduzir: o snap cria colisoes e a reducao seguinte
   gasta slots em ruido. Foi exatamente esse erro que levou o `r2-02` de 39 para
   47 cores.
4. Sem dithering por padrao. Dithering em espaco indexado gasta cor: cada padrao
   de dither precisa dos dois tons **ja presentes** na paleta.

**Criterio de valor em espaco indexado se expressa em degraus de paleta, nao em
float.** Errado: "luminancia media entre 0.24 e 0.27". Certo: "remapear para tons
ja existentes na paleta, 2 degraus abaixo da camada vizinha, zero cores novas".

---

## 2. A DECISAO DE SHADOW/HIGHLIGHT

A chamada mais consequente deste documento. Ela muda o significado do bit de
prioridade da tela inteira e por isso precede toda arte final.

### 2.1 O que o hardware faz `[VERIFICADO]` + `[DECIDIDO]`

API: `VDP_setHilightShadow(bool value)` — `sdk/sgdk-2.11/inc/vdp.h:832`.
**E um toggle global.** Nao existe S/H por tile, por plano ou por regiao.

Com S/H ligado, o bit de prioridade deixa de ser um seletor de camada e passa a
ser um seletor de brilho:

- tile de fundo com **priority = 0** renderiza a **meio brilho** (shadow)
- tile de fundo com **priority = 1** renderiza normal
- sprites com cores especiais da paleta 3 agem como **operadores**, escurecendo
  ou clareando o que esta embaixo em vez de desenhar

### 2.2 A decisao `[DECIDIDO]`

> **S/H LIGADO no jogo inteiro, sempre. Todo tile de fundo e autorado com
> priority = 1. Sem excecao, sem troca por cena.**

**Por que ligado:** o vortex de inalar e o verbo central do jogo. Kirby inala em
toda fase, toda sala, contra todo inimigo. Se o efeito de succao existe numa fase
e nao noutra, ele deixa de ser a identidade do personagem e vira enfeite de cena.
Alem dele, S/H paga por vidro, energia, holofote da arena do boss e fantasmas —
todos itens explicitos do brief.

**Por que global e nao por cena:** trocar S/H por cena tornaria a arte **nao
portavel entre cenas**. O mesmo tile renderiza com brilho diferente dependendo
da cena, e todo asset teria de ser autorado duas vezes ou revalidado por cena.
Um unico regime uniforme e a decisao mais barata de sustentar.

**O que isso custa, explicitamente:**

1. **O bit de prioridade dos tiles de fundo esta gasto.** Layering dentro do
   fundo passa a ser feito por ordem de plano (BG_A na frente de BG_B) e por
   prioridade de **sprite**, nunca por prioridade de tile.
2. **Todo tile de fundo com priority = 0 e um bug visual**, nao uma escolha.
   Aparece a meio brilho. Isso precisa ser um gate.
3. **Duas entradas de CRAM ficam reservadas** como operadores (§2.3).

### 2.3 Os operadores, e o custo real em cores

Em S/H, sprites que usam as duas ultimas entradas da paleta 3 agem como
operadores em vez de desenhar pixel:

| Slot | Papel |
|---|---|
| PAL3 indice 14 | operador de **highlight** — clareia o que esta embaixo |
| PAL3 indice 15 | operador de **shadow** — escurece o que esta embaixo |

Consequencia: **esses dois slots nao podem ser usados como cor normal em sprite.**

`[DECIDIDO]` Para eliminar ambiguidade, este projeto tambem **proibe** tile de
fundo de usar PAL3 indices 14 e 15 como cor. Tecnicamente seria possivel, mas
gera arte que se comporta diferente conforme desenhada em sprite ou em tile —
custo de confusao maior que o beneficio de 2 slots.

### 2.4 Correcao ao brief: o teto real e 58, nao 61

O brief do projeto diz "Max. 61 cores simultaneas". Contabilidade honesta:

```
64   entradas de CRAM (4 paletas x 16)
-4   indice 0 de cada paleta = transparente
-2   PAL3 indices 14 e 15 = operadores de S/H
----
58   cores utilizaveis simultaneamente
```

`[DECIDIDO]` **O teto deste projeto e 58.** Regra dura 4 do brief: medicao
contradiz o brief, segue a medicao e documenta. Aqui nao foi medicao e sim
aritmetica de hardware, mas a regra vale igual.

`gates.py` hoje testa contra 61. **Precisa ser atualizado para 58** e para
tratar PAL3[14] e PAL3[15] como reservados. Registrado em §7.

---

## 3. Alocacao de PAL0-PAL3

`[DECIDIDO]` Papel fixo por paleta no jogo inteiro. Papel fixo e o que permite
que tile de uma fase seja reaproveitado noutra sem retrabalho de indice.

| Paleta | Papel | Dono do conteudo |
|---|---|---|
| **PAL0** | Fundo distante — ceu, montanhas, colinas (camadas 1-3) | cena |
| **PAL1** | Fundo proximo — terreno jogavel, blocos, agua (camada 4) | cena |
| **PAL2** | Kirby + HUD + inimigos comuns | global, quase imutavel |
| **PAL3** | Habilidade ativa + FX + boss + operadores S/H | habilidade/boss |

### 3.1 Por que PAL2 e quase imutavel

Kirby aparece em todas as cenas e a rampa dele foi canonizada no loop de arte.
Se PAL2 muda por cena, Kirby muda de cor por cena. PAL2 e travada:

```
PAL2[0]   transparente
PAL2[1]   255,219,255   rosa highlight
PAL2[2]   255,182,219   rosa claro      <- carrega o corpo (49% da area medida)
PAL2[3]   255,146,182   rosa base
PAL2[4]   219, 73,146   rosa sombra
PAL2[5]   146, 36,109   rosa profundo
PAL2[6]   109, 36, 73   contorno
PAL2[7]   219, 73, 73   pe claro
PAL2[8]   146, 36, 36   pe escuro
PAL2[9]    36, 36, 73   olho
PAL2[10]  255,255,255   brilho do olho / branco de HUD
PAL2[11]  ...           HUD: fundo de barra
PAL2[12]  ...           HUD: preenchimento de vida
PAL2[13]  ...           inimigo comum A
PAL2[14]  ...           inimigo comum B
PAL2[15]  ...           inimigo comum C
```

Indices 1-10 vem da rampa canonica corrigida no loop de arte
(`doc/art/R2_VERDICT_AND_R3_PACK.md` §5). **Ja verificada em arte real:** os 5
tons presentes, zero tom da rampa salmao antiga. Indices 11-15 `[NAO MEDIDO]`,
dependem do HUD e do roster de inimigos.

### 3.2 A escada de valor das camadas — normativa

Medida e aprovada no loop de arte, formula canonica sRGB
(`doc/art/R2_VERDICT_AND_R3_PACK.md` §8.1):

| Camada | Fonte | Paleta | Luminancia media alvo |
|---|---|---|---|
| 1 ceu | BG_B banda 0 | PAL0 | **0.734** |
| 2 montanhas | BG_B banda 1 | PAL0 | **0.502** |
| 3 colinas | BG_B banda 2 | PAL0 | **0.453** |
| 4 terreno | BG_A | PAL1 | **0.340** |
| 5 primeiro plano | sprites | PAL1 | **0.258** |

**Monotonicamente decrescente do fundo para a frente.** Isso e o que faz o
primeiro plano ler como o mais proximo da camera.

Ponto fragil conhecido e registrado: o gap camada 2 -> 3 e de apenas 0.049.
Elas se separam tambem por **saturacao** (0.269 contra 0.339), que e a ferramenta
correta de perspectiva atmosferica. Reavaliar quando existir tile real na ROM.

**Gate derivavel disto:** a escada tem de permanecer monotonica. Camada mais
proxima com luminancia maior que a anterior e reprovacao, nao gosto.

---

## 4. Tabelas por cena

### 4.1 Fase 1 — Vegetable Valley `[DECIDIDO]`

PAL0, fundo distante — deriva do `r1-02/layers.png` aprovado:

```
PAL0[0]   transparente
PAL0[1-6]   ceu, 6 tons, do topo (mais claro) ao horizonte (creme)
PAL0[7]     nuvem branca
PAL0[8]     nuvem sombra
PAL0[9-10]  montanha distante, 2 tons roxo-azulados dessaturados
PAL0[11-13] colina, 3 tons de verde
PAL0[14]    tronco de arvore distante
PAL0[15]    contorno de fundo
```

PAL1, fundo proximo:

```
PAL1[0]     transparente
PAL1[1-3]   topo de grama, 3 tons de verde brilhante
PAL1[4-6]   corpo de terra, 3 tons de marrom
PAL1[7]     contorno de terreno
PAL1[8-10]  cachoeira, 3 tons — RESERVADO PARA CICLO (ver §5)
PAL1[11]    pedra
PAL1[12]    flor A
PAL1[13]    flor B
PAL1[14-15] primeiro plano (camada 5), 2 tons de verde escuro
```

O ceu usa **6 slots de paleta** mas produz **11 faixas visiveis** na tela,
porque as faixas extras vem de troca de cor por H-int, nao de slots adicionais.
Essa e a economia central do projeto: **faixa de raster e barata em CRAM e cara
em CPU; slot de paleta e o contrario.**

### 4.2 Arena do boss — Whispy Woods `[DECIDIDO]`

PAL3 muda de dono: aqui e do boss, nao da habilidade. Consequencia de design
declarada: **na arena do boss o Kirby luta com a habilidade que trouxe, mas o FX
dela usa a rampa reduzida de PAL2**, porque PAL3 esta ocupada.

```
PAL3[0]     transparente
PAL3[1-4]   casca do tronco, 4 tons de marrom
PAL3[5-7]   folhagem, 3 tons de verde
PAL3[8]     branco do olho
PAL3[9]     iris
PAL3[10]    sobrancelha / contorno de rosto
PAL3[11]    maca (projetil)
PAL3[12-13] rajada de ar, 2 tons
PAL3[14]    OPERADOR DE HIGHLIGHT — holofote da arena
PAL3[15]    OPERADOR DE SHADOW — vortex de inalar
```

13 cores de conteudo + 2 operadores. Confere com a arte aprovada: o `r2-03`
entregou exatamente **13 cores** depois de eu pedir folga para o flash de dano.
O flash de dano usa troca de PAL3 por 2 frames, nao sprite branco
(ARCHITECTURE.md §7).

---

## 5. Palette cycling

`[DECIDIDO]` Ciclo e rotacao de N slots contiguos dentro de uma paleta. Custo:
N escritas de CRAM por frame de ciclo.

| Efeito | Cena | Slots | Periodo |
|---|---|---|---|
| Cachoeira | fase 1 | PAL1[8-10] | 3 slots, avanca a cada 6 frames |
| Superficie de agua | fase 2 | PAL1[8-11] | 4 slots, a cada 8 frames |
| Neon / cristal | fase 3 | PAL0[11-13] | 3 slots, a cada 4 frames |

Custo de CRAM por frame no pior caso: 4 words. Desprezivel contra o orcamento de
DMA. **Ciclo nunca cruza fronteira de paleta** — rotacao dentro de um bloco de 16.

`[NAO MEDIDO]` Custo de CPU do ciclo. Deve ser trivial, mas trivial nao medido
segue sendo nao medido.

---

## 6. Troca de paleta por faixa no H-int

Coordenado com ARCHITECTURE.md §4: **um unico callback de H-int, teto de 16
faixas ativas por cena.**

### 6.1 Quantas words de CRAM cabem num hblank

`[NAO MEDIDO]` — **e este e o numero mais importante que ainda nao temos.**

O que se sabe com seguranca: o hblank e curto, e escrita de CRAM fora do
blanking gera lixo visivel em hardware real. Portanto o desenho e conservador
por construcao:

`[DECIDIDO]` **Cada faixa de H-int escreve no maximo 1 word de CRAM.**

Um efeito que precise de 6 cores novas numa faixa nao existe neste projeto. O
gradiente de ceu funciona porque cada faixa muda **uma** cor — a cor do ceu —
e nao a paleta inteira.

Medicao que resolve: cena de teste com N faixas escrevendo N words, aumentando N
ate aparecer lixo na captura do BlastEm, com confirmacao em hardware real via
flashcart. Enquanto isso nao existir, o teto de 1 word por faixa fica.

### 6.2 Catalogo de faixas do VER.001

| # | Efeito | Cena | Faixas | O que escreve |
|---|---|---|---|---|
| R1 | Gradiente de ceu | externas | 11 | cor de fundo / PAL0[1] |
| R2 | Bandas de parallax | todas | 3 | tabela de HScroll, nao CRAM |
| R3 | Distorcao de agua | fase 2 | por linha | tabela de HScroll |
| R4 | Faixa submersa | fase 2 | 1 | troca de PAL1 na linha d'agua |
| R5 | Holofote | boss | 2 | operador de highlight, nao CRAM |

R1 com 11 faixas e R4 com 1 = 12 faixas de CRAM, dentro do teto de 16. R2/R3/R5
nao gastam faixa de CRAM. **O orcamento fecha, no papel.**

### 6.3 Regra de derivacao da paleta submersa

O estudo `r1-06` propos, e a proposta e boa:

> para cada cor de superficie nao branca, mover G e B um degrau para cima, mover
> R um degrau para baixo, reduzir o valor maximo um degrau; branco permanece

`[DECIDIDO]` **Isso vira tabela estatica de 16 -> 16 words compilada em ROM, nao
operacao aritmetica em runtime.** O proprio Codex apontou o motivo, e ele esta
certo: operacao cega achata materiais diferentes na mesma cor. A tabela e
autorada a mao a partir da PAL1 de superficie e revisada visualmente.

Custo em runtime: 1 troca de paleta na linha d'agua = 16 words por DMA em VBlank,
mais 16 words na volta. Nao no H-int.

---

## 7. Gates — o que `gates.py` precisa checar

| # | Gate | Regra | Estado hoje |
|---|---|---|---|
| P1 | CRAM legal | `(word & ~0x0EEE) == 0` para as 64 entradas | **implementado** |
| P2 | Teto de cores | <= **58** distintas nao transparentes | **implementado com 61 — CORRIGIR** |
| P3 | Operadores reservados | PAL3[14] e PAL3[15] nunca usados como cor | **ausente — IMPLEMENTAR** |
| P4 | S/H ligado | registro de S/H ativo em toda cena | **ausente — IMPLEMENTAR** |
| P5 | Prioridade de tile | zero tile de fundo com priority = 0 | **ausente — IMPLEMENTAR** |
| P6 | Escada de valor | luminancia monotonica decrescente camada 1 -> 5 | **ausente — IMPLEMENTAR** |
| P7 | PAL2 travada | PAL2[1-10] identica a rampa canonica em toda cena | **ausente — IMPLEMENTAR** |

P2 e uma correcao de teto que solta um falso "pass" hoje: uma cena com 60 cores
passaria em 61 e violaria o limite real de 58.

P4 e P5 exigem ler o registro 0x0C e os bits de prioridade do nametable no
`visual_vdp_dump.bin`. O probe VLAB ainda **nao** exporta isso. E trabalho de
probe, nao de gate. Registrado como dependencia.

---

## 8. Criterio de pronto do subsistema de cor

- [ ] toda entrada de CRAM legal em RGB333, em toda cena — P1
- [ ] <= 58 cores simultaneas, em toda cena — P2
- [ ] PAL3[14] e PAL3[15] livres de uso como cor — P3
- [ ] S/H confirmado ligado em captura — P4
- [ ] zero tile de fundo com priority = 0 — P5
- [ ] escada de valor monotonica — P6
- [ ] PAL2[1-10] identica em todas as cenas — P7
- [ ] gradiente de ceu com 11 faixas visiveis, zero lixo na fronteira — captura
- [ ] troca de paleta submersa sem tearing na linha d'agua — captura
- [ ] `[NAO MEDIDO]` words de CRAM por hblank, com prova em hardware real

Os tres ultimos **nao sao verificaveis por script**. Exigem captura e olho.

---

## 9. Changelog

| Data | Mudanca |
|---|---|
| 2026-07-29 | v1. Layout de CRAM verificado em `pal.h:18-26`. **S/H decidido: ligado globalmente, todo tile de fundo priority=1.** Teto de cores corrigido de 61 para **58** por causa dos 2 operadores. PAL0-PAL3 alocadas com papel fixo. PAL2 travada na rampa canonica vinda do loop de arte. Escada de valor de 5 camadas importada como normativa. Teto conservador de 1 word de CRAM por faixa de H-int enquanto nao houver medicao. 7 gates especificados, 2 implementados. |
