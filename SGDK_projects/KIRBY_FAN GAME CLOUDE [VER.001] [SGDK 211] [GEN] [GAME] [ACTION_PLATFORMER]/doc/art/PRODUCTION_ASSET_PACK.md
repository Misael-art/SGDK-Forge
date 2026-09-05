# PRODUCTION ASSET PACK — todos os assets do jogo, de uma vez

> **Para quem:** agente de IA com capacidade de gerar imagens (Codex).
> **De quem:** agente diretor deste projeto.
> **Rodada:** P1 (producao). Diferente de R1/R2/R3, que eram **arte conceitual**.
> **Projeto:** KIRBY_FAN GAME CLOUDE [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

---

## 0. O QUE MUDOU DESDE A RODADA R1 — LEIA PRIMEIRO

O pacote R1 pedia **arte conceitual** e proibia explicitamente os papeis
`animated_sprite_final`, `hud_final` e `res_direct`. Este pacote pede **o
oposto**: assets finais, na grade nativa, prontos para entrar em `res/`.

Essa inversao tem justificativa medida, nao e otimismo:

> As 11 entregas de R1/R2/R3 chegaram com **0.00% de pixels ilegais** em RGB333,
> na primeira rodada, e o R3 fechou com paleta reduzida sem cor nova. Voce provou
> que consegue entregar pixel-exato quando recebe restricao exata. Por isso agora
> a restricao vem exata e o pedido e final.

**O jogo ja roda por inteiro.** Titulo, fase, lago, boss, game over, 5 copy
abilities, audio, e os 5 efeitos raster — tudo com gates passando. O que ele NAO
tem e arte: cada asset abaixo e hoje um placeholder desenhado por script Python.
Voce esta substituindo bonecos por arte, num jogo que funciona.

---

## 1. AS TRES REGRAS QUE INVALIDAM A ENTREGA

### 1.1 Dimensao EXATA, sem excecao

Cada arquivo abaixo tem largura e altura fixas. **`res/resources.res` declara o
tamanho do sprite em tiles e o codigo indexa os frames por posicao.** Um pixel a
mais ou a menos quebra o build ou desalinha toda a animacao.

Nao "melhore" a resolucao. Nao adicione margem. Nao centralize diferente.

### 1.2 A chave de transparencia e uma cor RESERVADA

`255, 0, 255` (magenta puro). Ela **nao pode participar da quantizacao**.

Isso ja falhou uma vez: no R1-03 o quantizador moveu o fundo para `(255,0,219)`
em 56% dos pixels e criou tres magentas coexistindo. Trate a chave como cor fixa,
excluida do algoritmo, e verifique que ela aparece com valor exato.

Se a arte precisar de roxo, use `(182,73,182)` ou `(146,36,146)` — nunca algo
proximo da chave.

### 1.3 A grade de cor do VDP

Cada canal so pode assumir estes 8 valores:

```
0   36   73   109   146   182   219   255
```

**Todos os tres canais de toda cor.** Nao existe 200. Existe 182 e existe 219.

---

## 2. AS PALETAS SAO CONTRATO, NAO SUGESTAO

O jogo tem 4 paletas de 16 cores. `doc/PALETTES.md` trava o papel de cada uma, e
cada asset abaixo declara **qual paleta usa**. Voce nao escolhe.

### 2.1 PAL2 — Kirby, e ela e IMUTAVEL

Esta rampa foi corrigida no loop R1→R2 (a original era salmao, nao rosa
chiclete) e depois **verificada em arte real**. Ela nao muda:

```
indice  cor            papel
  1     255,219,255    highlight
  2     255,182,219    claro      <- carrega o corpo (49% da area)
  3     255,146,182    base
  4     219, 73,146    sombra
  5     146, 36,109    profundo
  6     109, 36, 73    contorno
  7     219, 73, 73    pe claro
  8     146, 36, 36    pe escuro
  9      36, 36, 73    olho
 10     255,255,255    brilho do olho
```

Medicao do R2 que voce deve repetir: o **meio-tom (indice 3) precisa ocupar 8 a
12% da area do corpo**. Na primeira entrega ele ficou em 0.58% e o Kirby leu
chapado — a forma esferica estava sendo resolvida com dois tons em vez de tres.

### 2.2 PAL0 — fundo distante. A escada de valor e normativa

Medida e aprovada no R3, formula sRGB `L = (0.2126R + 0.7152G + 0.0722B)/255`:

| camada | luminancia alvo |
|---|---|
| 1 ceu | **0.734** |
| 2 montanhas | **0.502** |
| 3 colinas | **0.453** |
| 4 terreno (PAL1) | **0.340** |
| 5 primeiro plano (PAL1) | **0.258** |

**Monotonicamente decrescente do fundo para a frente.** E o que faz o primeiro
plano ler como o mais proximo da camera. Camada mais proxima com luminancia
maior que a anterior e reprovacao.

Ponto fragil conhecido: o gap camada 2 -> 3 e de so 0.049. Elas tambem se separam
por **saturacao** (0.269 contra 0.339). Mantenha essa diferenca.

### 2.3 PAL3 — habilidades e boss. DOIS INDICES SAO PROIBIDOS

```
PAL3 indice 14  = OPERADOR DE HIGHLIGHT
PAL3 indice 15  = OPERADOR DE SHADOW
```

O jogo roda com Shadow/Highlight ligado globalmente. Nesse modo, um sprite que
use esses dois indices **nao desenha cor**: ele clareia ou escurece o que esta
embaixo. E a unica pseudo-transparencia real do Mega Drive e o jogo ja usa isso
no holofote do boss.

**Nenhum asset pode usar PAL3[14] ou PAL3[15] como cor normal.**

### 2.4 Teto de cores

**58 cores simultaneas na tela**, nao 61: sao 64 entradas, menos 4 transparencias,
menos os 2 operadores acima.

---

## 3. FORMATO DE ENTREGA

```
<projeto>/data/source_art/p1/<id>/
    <nome_exato>.png     o asset, na dimensao exata
    notes.md             autocritica honesta + contagem de cores real
    prompt_used.txt      o prompt literal
```

- PNG, sem perda, alpha 0 ou 255 apenas
- **Nearest neighbour** em qualquer escala. Borda borrada mata a traducao
- Sem marca d'agua, sem assinatura, sem moldura, sem texto (exceto o logo)
- Em `notes.md`: **conte as cores de verdade**, e diga do que voce nao gostou

---

## 4. OS ASSETS

### Grupo A — Personagem (prioridade MAXIMA)

#### A1 · `ph_kirby.png` — **256 x 32** · PAL2 · max 15 cores

Folha de **8 frames de 32x32**, lado a lado, nesta ordem exata. O codigo indexa
por posicao (`src/entities/kirby.c`):

| # | frame | estado |
|---|---|---|
| 0 | IDLE | parado, respirando |
| 1 | RUN 1 | corrida, contato |
| 2 | RUN 2 | corrida, passagem |
| 3 | RUN 3 | corrida, contato oposto |
| 4 | RUN 4 | corrida, passagem oposta |
| 5 | JUMP | no ar, subindo |
| 6 | FLOAT | bochechas infladas, flutuando |
| 7 | INHALE | boca muito aberta, corpo inclinado para tras |

Kirby olha para a **direita**; o codigo espelha por hardware.

**Frame 6 (FLOAT) e o que ja falhou.** Na entrega R1 as bochechas ficaram dentro
da massa do corpo e sumiram a 28 px. A correcao aprovada foi: **a bochecha
estoura para FORA do circulo do corpo**, criando duas protuberancias na silhueta,
com contorno proprio em `(109,36,73)`.

**Teste de aceite:** reduzido a 32 px, a silhueta preta do frame 6 tem de ser
distinguivel da do frame 0 **so pelo contorno**.

#### A2 · `ph_enemy.png` — **32 x 16** · PAL2 · max 8 cores

2 frames de 16x16: andando, pe A e pe B. Criatura redonda, simples, com olhos
grandes e pes pequenos. Le a 16 px — detalhe facial que nao cabe em 3 pixels de
altura nao existe.

Usa PAL2 (indices 13-15 estao livres para ele). Nao pode conflitar com o Kirby.

#### A3 · `ph_particle.png` — **24 x 8** · PAL2 · max 4 cores

3 frames de 8x8: estrela encolhendo (grande, media, pequena). Usada nas
particulas de inalar. Legivel a 8 px = essencialmente 3 ou 4 pixels acesos.

---

### Grupo B — Fase 1, Vegetable Valley

Todos com **512 px de largura** (a largura do plano) e altura fixa. Sao faixas
horizontais que ladrilham no eixo X: **a borda esquerda tem de casar com a
direita sem costura.**

#### B1 · `ph_sky.png` — **512 x 80** · PAL0 · max 6 cores

Nuvens redondas e gordas sobre fundo TRANSPARENTE (chave magenta).

**O ceu em si NAO e desenhado aqui.** Ele e o backdrop, pintado por um gradiente
de 12 faixas via H-interrupt. Este arquivo tem so as nuvens. Onde nao ha nuvem,
magenta.

#### B2 · `ph_mount.png` — **512 x 56** · PAL0 · max 4 cores · luminancia **0.502**

Montanhas distantes. **Dessaturadas e claras** — perspectiva atmosferica e a
ferramenta principal. Fundo magenta acima da linha das montanhas.

#### B3 · `ph_hills.png` — **512 x 88** · PAL0 · max 6 cores · luminancia **0.453**

Colinas com arvores de copa esferica. Mais saturadas que B2 e mais escuras.
Fundo magenta acima.

#### B4 · `ph_terrain.png` — **512 x 64** · PAL1 · max 10 cores · luminancia **0.340**

Terreno jogavel: topo de grama e corpo de terra. **Alinhado a grade de 8 px.**

Deixe **dois vaos** (sem terreno, magenta ate embaixo) em `x = 160..208` e
`x = 320..352` — o codigo usa esses vaos como buracos jogaveis e o teste de
gate os procura.

**Solido pisavel tem de ser distinguivel de decoracao SO PELO VALOR.** Erro aqui
vira morte injusta.

#### B5 · `ph_fg.png` — **32 x 16** · PAL1 · max 4 cores · luminancia **0.258**

Um tufo de grama de primeiro plano, 1 frame. Passa NA FRENTE do Kirby, entao e
o elemento **mais escuro da tela**. Verde profundo, quase silhueta.

---

### Grupo C — Boss, Whispy Woods

#### C1 · `ph_trunk.png` — **64 x 96** · PAL3 · max 6 cores

Tronco de arvore, tiles de fundo (nao sprite). Casca com sulcos verticais
grossos. Ladrilha verticalmente sem costura.

#### C2 · `ph_boss_face.png` — **96 x 32** · PAL3 · max 8 cores

2 frames de **48 x 32**: rosto calmo e rosto bravo. Olhos redondos grandes,
sobrancelhas grossas expressivas, nariz bulboso, boca. Legivel a 48 px de largura.

#### C3 · `ph_branch.png` — **16 x 16** · PAL3 · max 6 cores

**UM** segmento de galho, 1 frame. Cinco deles sao encadeados em runtime com
cinematica direta para formar um galho articulado.

**Restricao critica:** o segmento tem de funcionar isolado e em qualquer angulo.
Nada de detalhe que atravesse a fronteira do tile — ele sera rotacionado e
repetido. Simetrico no eixo horizontal.

#### C4 · `ph_apple.png` — **32 x 16** · PAL3 · max 5 cores

2 frames de 16x16: maca caindo, com leve oscilacao entre os frames. E o projetil
que o jogador inala e devolve como dano.

#### C5 · `ph_light.png` — **NAO DESENHE ESTE**

Ja existe e esta correto. E o operador de Shadow/Highlight: todo pixel opaco e o
indice 14, o que na pratica significa "clareia o que esta embaixo". Nao e arte,
e uma mascara. **Nao substitua.**

---

### Grupo D — Copy abilities

#### D1 · `ph_ability_fx.png` — **240 x 16** · PAL3 · max 14 cores

**15 frames de 16x16** = 5 abilities x 3 frames de animacao, nesta ordem:

| posicao x | ability | forma exigida |
|---|---|---|
| 0-47 | FIRE | pluma redonda que se abre |
| 48-95 | BEAM | raio irregular, angular, fino |
| 96-143 | CUTTER | crescente VAZADO (le como fio, nao como massa) |
| 144-191 | STONE | bloco de bordas duras, zero curvas |
| 192-239 | SWORD | arco fino e varrido |

**A forma e obrigatoria, nao decorativa.** Um jogador daltonico precisa
distinguir FIRE de SWORD sem ver a cor. Foi assim que o pedido R1-04 foi
aprovado e a regra continua.

Lembre: **indices 14 e 15 de PAL3 sao proibidos** (secao 2.3), entao voce tem
13 cores utilizaveis para as cinco abilities juntas.

---

### Grupo E — Tela de titulo

#### E1 · `ph_title_stars.png` — **512 x 96** · PAL0 · max 4 cores

Campo de estrelas sobre magenta. Estrelas em no maximo 3 tamanhos, todas
alinhadas a pixel. Ladrilha horizontalmente — ele faz drift lento.

#### E2 · `ph_title_hill.png` — **512 x 64** · PAL0 · max 5 cores

Silhueta de colina com uma arvore, escura, poucas cores. E uma silhueta: massa
solida, sem detalhe interno.

#### E3 · `ph_title_logo.png` — **224 x 48** · PAL1 · max 10 cores

O logotipo. **Este e o unico asset com texto.** Use a rampa de rosa canonica da
secao 2.1 para as letras.

Nao use tipografia ou marca da Nintendo. Letreiro autoral, no espirito do jogo:
gordo, arredondado, com contorno grosso e um brilho no topo.

---

## 5. COMO EU VOU JULGAR

Tudo abaixo e **medido por script**, nao por opiniao. O harness ja existe e ja
reprovou entregas antes.

| Criterio | Reprova quando |
|---|---|
| Dimensao | difere em 1 pixel do especificado |
| Grade RGB333 | qualquer canal fora dos 8 valores legais |
| Chave | qualquer magenta que nao seja exatamente `255,0,255` |
| Teto de cores | acima do maximo declarado por asset |
| Operadores | PAL3[14] ou PAL3[15] usados como cor |
| Escada de valor | luminancia nao monotonica entre camadas |
| Meio-tom do Kirby | indice 3 fora de 8-12% da area do corpo |
| Silhueta FLOAT | indistinguivel da IDLE em preto solido a 32 px |
| Ladrilhamento | costura visivel na juncao esquerda/direita |
| Vaos do terreno | ausentes em x=160..208 e x=320..352 |

O retorno vem quantificado, como nas rodadas anteriores:

> "B4 reprovado em escada de valor: terreno mediu 0.402, alvo 0.340, e ficou mais
> claro que as colinas (0.453 -> deveria ser mais escuro). Escureça dois degraus.
> B1, B2, B3 aprovados, nao mexa."

---

## 6. RESUMO OPERACIONAL

```
16 assets. Prioridade: A1 (Kirby) primeiro, depois grupo B, depois C, D, E.
NAO desenhe C5 (ph_light.png) — ja esta correto.

Saida: <projeto>/data/source_art/p1/<id>/{<nome>.png, notes.md, prompt_used.txt}

Cor: canais apenas em {0,36,73,109,146,182,219,255}
Chave: 255,0,255 EXATO, excluida da quantizacao
PAL3[14] e PAL3[15]: PROIBIDOS como cor
Dimensao: exata, um pixel de diferenca reprova
PNG, nearest neighbour, sem texto exceto E3

Em notes.md: conte as cores de verdade e diga do que voce nao gostou.
```

Se algum pedido for impossivel como escrito, **entregue o que for possivel e
diga o que nao foi** — nao invente conformidade. Foi assim que as rodadas
anteriores funcionaram.

---

## 7. Changelog

| Data | Mudanca |
|---|---|
| 2026-08-06 | P1 criada. 16 assets de producao com dimensao exata, paleta travada e criterio de aceite medivel. Substitui os placeholders programaticos num jogo que ja roda inteiro. |
