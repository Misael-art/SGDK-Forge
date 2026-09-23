# R2 — VEREDITO MEDIDO + PACOTE R3

> **Julgado em:** 2026-07-29
> **Metodo:** verificacao independente com PIL+numpy sobre o PNG entregue.
> Nao confiei no relatorio do Codex; medi de novo e comparei.
> **R1 preservado:** hashes de `r1/` inalterados ✓

---

## 1. Tabela de veredito

| ID | Cores | Ilegais | Criterio principal | Veredito |
|---|---|---|---|---|
| R2-01 floating + rampa | 12 / 15 | 0.00% | rampa nova 5/5, floating corrigido | **APROVADO** |
| R2-02 camada 5 | **47 / 45** | 0.00% | lum 0.2496, camadas 1-4 diff 0 | **APROVADO NA INTENCAO, REPROVADO NO TETO** |
| R2-03 re-key Whispy | 13 / 13 | 0.00% | chave unica, proibidas = 0 px | **APROVADO** |
| R2-04 franja | 13 / 13 | 0.00% | franja = 0 px | **APROVADO** |

---

## 2. R2-03 e R2-04 — aprovados, limpos

**R2-03.** Medido independentemente:

```
(255,   0, 255)   63.01%   chave unica
(255,   0, 219)        0   px   <- eliminada
(219,   0, 219)        0   px   <- eliminada
cores: 13 (teto 13)
```

Metodo declarado e verificado: `exact RGB replacement only; no geometry, crop,
or resampling`. A arte nao foi tocada, so o keying. Era exatamente o pedido.

Existe `(182,36,182)` em 0.55% — roxo de arte, nao chave. Distante o suficiente
de `(255,0,255)` para nenhum keyer confundir. Aceito.

**R2-04.** `(219,0,219)` = 0 px, `(219,36,182)` = 0 px, chave unica em 76.69%,
13 cores. Fronteira em degrau duro. Passa.

---

## 3. R2-01 — aprovado, e a correcao funcionou de verdade

**Rampa corrigida: adotada por inteiro.** Medido: os 5 tons novos presentes,
**zero** tom da rampa salmao antiga remanescente.

```
(255,219,255)   0.28%   highlight
(255,182,219)  49.20%   claro    <- carrega o corpo
(255,146,182)   2.58%   base
(219, 73,146)   6.48%   sombra
(146, 36,109)   0.61%   profundo
```

**Pose floating: consertada, e mensuravelmente.** Perfil de largura da silhueta
no downscale real para 28 px, em pixels por linha:

| | topo (linha 4) | meio (14) | base (24) |
|---|---|---|---|
| neutral | 20 | 33 | 27 |
| floating **R1** | **6** | 27 | 6 |
| floating **R2** | **19** | 28 | 9 |

A linha do topo saiu de 6 para 19 px. Era exatamente o defeito: a bochecha
inflada estava dentro da massa do corpo e nao existia na silhueta. Agora existe.
No teste em cor a 28 px as bochechas leem como duas massas separadas e os olhos
sobrevivem.

Criterio "distinguivel de neutral so pelo contorno": **passa**, mas nao pela
bochecha — passa pela base (27 px de dois pes plantados contra 9 px de um pe
recolhido). Anotado para nao virar falsa confianca.

---

## 4. R2-02 — o teto de cores estourou, e a culpa e do meu criterio

**O que passou, e passou bem:**

```
camada 5 luminancia:  0.3703 -> 0.2496   (janela pedida 0.24-0.27)  OK
camadas 1-4 pixel diff:  EXATAMENTE 0 px                            OK
pixels ilegais:          0.00%                                       OK
```

Isolamento perfeito. Pedi diff zero fora da camada 5 e recebi diff zero. Isso e
raro e merece registro.

**O que falhou:** 39 -> **47 cores**, teto 45. Zero cores removidas, 8 adicionadas.

**A causa esta declarada pelo proprio Codex**, no relatorio dele:

> `palette_snap_micro_dither: {pixels: 4454, purpose: "enter the requested
> luminance interval after discrete RGB333 snapping"}`

Ou seja: para caber na minha janela numerica de luminancia depois de arredondar
para a grade discreta de 8 niveis por canal, foi preciso adicionar micro-dither.
O micro-dither criou cores novas. As cores novas estouraram o teto.

**Isso e defeito do meu criterio, nao do trabalho.** Pedir uma janela apertada de
luminancia em ponto flutuante sobre um espaco de 512 cores discretas empurra o
executor para dithering. Das 8 cores novas, 5 sao ruido puro:

```
(36, 73, 73)     0.002%
(73, 73, 36)     0.002%
(73,109,109)     0.001%
(146,109,109)    0.002%
(146,146,109)    0.025%
```

Cinco slots de paleta gastos em pixels que ninguem ve. Apenas `(0,36,36)` 0.922%
e `(109,109,36)` 0.208% fazem trabalho visual.

**Nota lateral, benigna:** detectei 110.078 px de diferenca fora das bandas que eu
havia mapeado no R1 (linhas 730-895). Nao e defeito: a banda da camada 5 mudou de
extensao. Verifiquei antes de acusar.

---

## 5. Duas correcoes no MEU processo

Segunda rodada consecutiva em que o erro e meu. Registrando para nao repetir.

**5.1 Nao especifiquei a formula de luminancia.** Eu media com
`0.299R + 0.587G + 0.114B`. O Codex mediu com
`0.2126R + 0.7152G + 0.0722B` (sRGB). Mesma imagem, dois numeros: 0.2496 e
0.269899. Ambos caem na janela, entao nao houve dano — mas foi sorte.

**Daqui em diante, formula canonica do projeto:**
`L = (0.2126*R + 0.7152*G + 0.0722*B) / 255` — a do Codex, porque e a
perceptualmente correta para sRGB. Vai para o `PALETTES.md`.

**5.2 Criterio de luminancia deve ser em degraus, nao em float.** Em vez de
"luminancia media entre 0.24 e 0.27", o criterio correto num espaco discreto e:

> "remapear a camada 5 para tons **ja existentes na paleta**, escolhendo os que
> ficam 2 degraus abaixo dos da camada 4. Zero cores novas permitidas."

Isso obtem o mesmo resultado visual sem forcar dithering e sem gastar paleta.

**5.3 "Area do corpo" era ambiguo** no criterio de meio-tom. Eu medi sobre todos
os pixels nao-fundo (que incluem rotulos, pes, olhos e silhuetas) e achei 2.58%;
eles mediram sobre a regiao do corpo e acharam 10.00%. Nenhum dos dois esta
errado — o criterio estava. Como a intencao (forma esferica lendo redonda, nao
chapada) foi atingida no teste de 28 px, **aceito**.

---

## 6. PACOTE R3 — um item, cirurgico

| ID | Pedido | Criterio de aceite |
|---|---|---|
| **R3-02** | Reduzir a paleta do `r2-02/layers.png` | Colapsar as 5 cores de ruido (`(36,73,73)`, `(73,73,36)`, `(73,109,109)`, `(146,109,109)`, `(146,146,109)`) no vizinho mais proximo **ja presente** na paleta. Resultado: **<= 45 cores** (esperado 42). Luminancia da camada 5 pode variar dentro de **0.23-0.28**. Camadas 1-4 seguem com **pixel diff 0**. Zero cores novas. |

Nada mais. R2-01, R2-03 e R2-04 estao fechados.

---

## 7. Estado da arte apos R2

| Pedido | Estado |
|---|---|
| r1-05, r1-06, r1-07 | aprovados no R1, intactos |
| r2-01 (personagem) | **aprovado**, rampa canonica aplicada |
| r2-03 (Whispy) | **aprovado**, chave limpa |
| r2-04 (chapeus) | **aprovado**, sem franja |
| r2-02 (camadas) | **1 correcao pendente** (R3-02, teto de cores) |

Gate de legalidade RGB333: **11/11 entregaveis a 0.00%** somando R1 aprovados e R2.

**Nada promovido para `res/`.** Status segue `source_candidate`. A promocao
continua exigindo `PALETTES.md` (que agora tem duas entradas obrigatorias vindas
daqui: a formula de luminancia e a rampa de rosa canonica) e gate visual no
BlastEm.

---

## 8. R3-02 — VERIFICADO. APROVADO. Loop de arte ENCERRADO.

Verificacao independente, formula canonica sRGB:

```
cores:        R1=39  ->  R2=47  ->  R3=42        teto 45   OK
ilegais RGB333:                    0.00%                    OK
5 cores de ruido:                  0 px cada, todas removidas OK
cores novas vs R2:                 nenhuma                   OK
camadas 1-4 pixel diff vs R1:      EXATAMENTE 0              OK
```

Das 3 cores que R3 mantem acima do R1 — `(0,36,36)`, `(73,73,109)`,
`(109,109,36)` — todas fazem trabalho visual real. As cinco que nao faziam
sairam. Era exatamente o pedido.

### 8.1 A escada de valor, agora correta

Luminancia media por camada, formula canonica sRGB, no arquivo aprovado:

```
camada 1  ceu           0.7339
camada 2  montanhas     0.5024     gap -0.2315
camada 3  colinas       0.4526     gap -0.0498
camada 4  terreno       0.3401     gap -0.1125
camada 5  primeiro      0.2579     gap -0.0822
```

**Monotonicamente decrescente do fundo para a frente.** O primeiro plano e agora
o mais escuro, que e o que precisa acontecer para ele ler como o mais proximo da
camera enquanto passa na frente do heroi.

O gap mais estreito e camada 2 -> 3 (0.0498). Nao vou reabrir: essas duas foram
aprovadas no R1 e estao separadas tambem por saturacao (0.269 contra 0.339), que
e a ferramenta correta de perspectiva atmosferica. Fica registrado como o ponto
mais fragil da escada, para reavaliar quando existir tile real na ROM.

**Esta tabela e a referencia normativa de valor para o `PALETTES.md`.**

### 8.2 Por que o loop de arte para aqui

O brief manda rodar `/loop` "ate o critico hesitar ou errar".

Aconteceu, e de forma clara: nas tres ultimas rodadas os defeitos deixaram de
ser da arte e passaram a ser **dos meus criterios** — janela de luminancia em
float sobre grade discreta, formula de luminancia nao especificada, "area do
corpo" ambigua, rampa de rosa errada no contrato original. O executor entregou
exatamente o que foi pedido em todas elas.

Um critico que erra tres vezes seguidas sobre os proprios criterios, e nenhuma
sobre o trabalho, nao esta mais extraindo qualidade — esta gerando retrabalho.
**Encerro o loop de arte do escopo R1 aqui.**

Estado final: 7 pedidos, todos em `source_candidate`, todos legais em RGB333.

### 8.3 O que passa a ser o gargalo, e ele e meu

A arte conceitual nao pode avancar mais **porque o que falta nao e arte**:

1. `doc/PALETTES.md` nao existe. Sem ele nao ha alocacao PAL0-PAL3, nao ha
   decisao de Shadow/Highlight e nao ha tabela de derivacao submersa. Ele nasce
   com tres entradas obrigatorias vindas deste loop: a formula de luminancia
   canonica, a rampa de rosa do protagonista e a escada de valor de 8.1.
2. `doc/VRAMMAP.md` nao existe. Sem ele nao se sabe quantos tiles cada camada
   pode custar, e o gate `vram_tile_budget` segue em `warn`.
3. Nenhuma dessas imagens foi vista rodando em ROM. Pela regra de ferro do
   workspace — "se nao foi visto rodando no emulador, nao existe" — a arte
   aprovada aqui ainda nao existe como asset.

Proximo passo do projeto nao e R4. E `PALETTES.md`.

---

## 9. Changelog

| Data | Mudanca |
|---|---|
| 2026-07-29 | R2 julgada por medicao independente. 3 de 4 aprovados. R2-02 aprovado na intencao mas reprovado no teto de cores (47/45), causa autodeclarada: micro-dither para caber na minha janela de luminancia. Formula de luminancia canonizada. Criterio de luminancia migrado de float para degraus de paleta. R3 emitida com 1 item. |
| 2026-07-29 | R3-02 verificado e aprovado: 42 cores, 0 cores de ruido, 0 cores novas, camadas 1-4 com diff 0, escada de valor monotonica. **Loop de arte do escopo R1 encerrado** por criterio do brief (critico passou a errar sobre os proprios criterios). Gargalo transferido para `PALETTES.md` e `VRAMMAP.md`. |
