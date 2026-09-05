# AI IMAGE PROMPT PACK — Round 1

> **Para quem:** agente de IA com capacidade de gerar imagens (Codex).
> **De quem:** agente diretor de arte deste projeto.
> **Rodada:** R1. Nao ha rodada 2 ate que R1 seja julgada.
> **Projeto:** KIRBY_FAN GAME CLOUDE [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

---

## 0. LEIA ISTO ANTES DE GERAR QUALQUER COISA

### 0.1 O que voce esta produzindo, e o que voce NAO esta produzindo

Voce esta produzindo **arte conceitual e estudos de estilo** que serao depois
traduzidos a mao para tiles/sprites de Mega Drive.

Voce **nao** esta produzindo assets finais. Nenhuma imagem sua entra na ROM
diretamente. Isso nao e uma limitacao do seu talento — e que gerador de imagem
nao acerta grade de 8x8, deduplicacao de tile, indice de paleta de 4 bpp e
limite de 20 sprites por scanline. Essa parte e feita depois, por outro passo do
pipeline.

Papeis permitidos nesta rodada, e so estes:

```
concept_art        arte conceitual de cena/personagem
tileset_concept    folha de vocabulario de terreno
contrast_study     estudo de valor/legibilidade
palette_study      estudo de cor dentro da grade legal do VDP
layer_study        separacao de camadas de parallax
```

Papeis proibidos: `animated_sprite_final`, `hud_final`, `res_direct`,
`aaa_final_asset`. Se um pedido abaixo parecer estar te empurrando para um
desses, pare e reporte em vez de entregar.

### 0.2 Aviso de direitos

Kirby e propriedade da Nintendo / HAL Laboratory. Este e um **fan game nao
comercial**. Portanto:

- Produza arte **original**, desenhada do zero, na linguagem visual do
  personagem. Nao reproduza, decalque ou faca upscale de sprites/artes oficiais.
- Nao use logotipos, tipografia ou marcas da Nintendo.
- Nada aqui sera vendido ou distribuido como produto.

### 0.3 A restricao de cor, que e a coisa mais importante deste documento

O VDP do Mega Drive tem **3 bits por canal**. Cada canal so pode assumir 8
valores. Traduzidos para 8 bits, os unicos valores legais sao:

```
0   36   73   109   146   182   219   255
```

**Toda cor que voce usar precisa ter os tres canais dentro dessa lista.**
Nao existe 200. Nao existe 128. Existe 182 e existe 146.

Alem disso:

- 4 paletas de 16 cores. O indice 0 de cada paleta e transparente.
- Teto de **61 cores simultaneas na tela inteira** (4 x 16 = 64, menos as
  transparencias uteis).
- Um tile de 8x8 so pode usar **uma** paleta. Isso significa que gradiente suave
  atravessando objetos diferentes nao existe.
- Nao existe alpha blending. Transparencia e feita com Shadow/Highlight, que
  escurece ou clareia — nao mistura.

Se voce entregar concept art com 4000 cores e gradiente aerografado, ela e
inutil para este projeto, por mais bonita que seja. **Trabalhe dentro da grade.**

### 0.4 Escala real, que e a segunda coisa mais importante

A tela e **320 x 224 pixels**. Isso e minusculo. Referencias de tamanho:

| Elemento | Tamanho real |
|---|---|
| Kirby | ~28 x 28 px |
| Inimigo comum | 16 x 16 a 24 x 24 px |
| Tile de terreno | 8 x 8 px |
| Whispy Woods (boss) | ~120 x 160 px |
| Altura util da tela (sem HUD) | ~192 px |

Consequencia dura: **silhueta manda em tudo.** Se o personagem nao for
reconhecivel como uma mancha preta de 28 px, nenhum detalhe interno salva.
Detalhe facial que nao cabe em 4 pixels de altura nao existe.

---

## 1. A IDENTIDADE VISUAL QUE ESTAMOS PERSEGUINDO

### 1.1 A tese

Kirby's Adventure (NES, 1993) foi um jogo que **tentou** coisas que o NES nao
suportava: ceu em gradiente, camadas de profundidade, cor por regiao. Ele
resolvia isso com truques de atributo e bankswitching, e o resultado era
encantador mas visivelmente comprimido.

Nosso trabalho e entregar **o que aquele jogo estava alcancando**, com o
vocabulario do Mega Drive.

Portanto, ao desenhar qualquer cenario, responda mentalmente:
**"o que o NES nao conseguiu fazer aqui?"** — e desenhe isso.

### 1.2 O tom

- Doce, pastel, arredondado, macio. Nada de grimdark. Nada de realismo.
- Motivo de estrela recorrente. Formas com contorno grosso e interior simples.
- Ceu e o personagem coadjuvante do jogo inteiro. Ele nunca e chapado.
- Perigo e comunicado por **forma e cor**, nunca por escuridao.

### 1.3 Referencias de qualidade tecnica (nao de conteudo)

Estes sao os jogos cujo **nivel de execucao** estamos perseguindo. Nao copie o
conteudo deles; entenda por que eles impressionam:

- **Ranger X** — profundidade de fundo por scroll de linha; cada faixa da tela
  se move numa velocidade diferente
- **Gunstar Heroes / Alien Soldier** — bosses gigantes feitos de muitas pecas
  articuladas
- **Castlevania: Bloodlines** — ceu em gradiente raster, atmosfera por cor
- **Dynamite Headdy** — cenarios com personalidade de brinquedo/palco
- **Demons of Asteborg, Xeno Crisis** — o teto atual do homebrew moderno

---

## 2. FORMATO DE ENTREGA (obrigatorio)

### 2.1 Onde salvar

```
<projeto>/data/source_art/r1/<id_do_pedido>/
    concept.png              imagem principal
    prompt_used.txt          o prompt exato que voce usou
    notes.md                 decisoes que voce tomou e por que
```

`<projeto>` = `SGDK_projects/KIRBY_FAN GAME CLOUDE [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]/`

### 2.2 Regras de arquivo

- PNG, sem perda, sem alpha parcial (alpha 0 ou 255 apenas).
- Fundo de personagem: magenta puro `255, 0, 255` como chave de transparencia.
- **Nao redimensione com interpolacao suave.** Se precisar escalar, use vizinho
  mais proximo (nearest neighbor). Borda borrada mata a traducao para tile.
- Sem marca d'agua, sem assinatura, sem borda decorativa, sem moldura.
- Sem texto na imagem, exceto onde o pedido pedir explicitamente.

### 2.3 O que colocar em `notes.md`

Seja breve e direto:

- quantas cores distintas a imagem tem de fato (conte, nao estime)
- quais decisoes voce tomou que fogem do pedido, e por que
- o que voce acha que vai quebrar quando isso virar tile de 8x8
- do que voce nao gostou no proprio resultado

Essa ultima linha e a mais util de todas. Autocritica honesta acelera a rodada 2.

---

## 3. OS PEDIDOS DA RODADA 1

Sete pedidos. Ordem de prioridade: **R1-01 e R1-02 primeiro.** Se o orcamento
acabar, prefira entregar tres pedidos bem resolvidos a sete medianos.

---

### R1-01 — Folha de personagem do heroi `concept_art`

**Canvas:** 1024 x 768, fundo magenta `255,0,255`
**Cores:** maximo 15 + transparencia
**Prioridade:** MAXIMA

Uma folha de estudo do heroi: uma criatura esferica rosa, ~28 px de altura no
jogo, mas desenhada aqui grande o suficiente para ser legivel.

Conteudo da folha, em grade organizada e rotulada:

1. **Pose neutra**, tres quartos, tamanho grande (ocupando ~1/3 da folha)
2. **Turnaround**: frente, tres quartos, perfil, costas
3. **Cinco expressoes**: neutro, determinado, surpreso, machucado, contente
4. **Tres poses de acao**: corrida, pulo/flutuando com bochechas infladas,
   inalando (boca muito aberta, corpo inclinado para tras)
5. **Estudo de silhueta**: as mesmas tres poses de acao, em preto solido puro,
   lado a lado

A criatura: corpo esferico rosa, dois pes ovais vermelho-escuros, bracos curtos
sem dedos como tocos arredondados, dois olhos ovais verticais escuros com um
brilho branco, dois blushes ovais rosa-escuros nas bochechas. Sem boca visivel
quando neutro. Contorno escuro definido, interior com no maximo 3 tons de rosa.

**Restricoes duras:**
- Rosa: use exatamente estes tres tons e nada entre eles — `255,182,182`,
  `255,146,146`, `219,109,146`
- Contorno: `109,36,73`
- Pes: `219,73,73` e `146,36,36`
- Olhos: `36,36,73` com brilho `255,255,255`
- Nada de aerografo. Nada de gradiente suave. Blocos de cor com borda nitida.
- A sombra de forma vem de **um** tom mais escuro, nao de um degrade.

**O que sera julgado:** a silhueta preta funciona? As tres poses de acao sao
distinguiveis so pela mancha? O personagem parece macio sem usar gradiente?

---

### R1-02 — Chave de cena e estudo de camadas: Fase 1 `layer_study`

**Canvas:** 1280 x 896 (= 320x224 x4), sem magenta, cena completa
**Cores:** maximo 45
**Prioridade:** MAXIMA

Uma cena de vale campestre doce e ensolarado, vista lateral de plataforma 2D.

**Entregue DUAS imagens neste pedido:**

**(a) `concept.png`** — a cena composta, como o jogador veria.

**(b) `layers.png`** — a MESMA cena, separada em 5 faixas horizontais
empilhadas e rotuladas, cada uma mostrando so aquela camada sobre fundo neutro:

```
CAMADA 1  ceu           gradiente vertical, do topo ao horizonte, ESTATICO
CAMADA 2  montanhas     silhuetas distantes, azuladas pela atmosfera
CAMADA 3  colinas       arvores redondas e colinas, mais saturadas
CAMADA 4  terreno       plataformas jogaveis, onde o heroi pisa
CAMADA 5  primeiro plano  folhagem/grama que passa NA FRENTE do heroi
```

Essa separacao **nao e decorativa** — cada camada vira uma velocidade de scroll
diferente no motor. Se as camadas nao forem separaveis, a cena e inutil.

**Conteudo:** ceu azul-claro em gradiente indo para amarelo-creme perto do
horizonte. Nuvens redondas e gordas. Montanhas roxo-azuladas ao longe.
Arvores de copa esferica em verdes chapados. Terreno com topo de grama verde
brilhante e corpo de terra marrom. Flores simples. Uma cachoeira estreita
caindo por tras do terreno.

**Restricoes duras:**
- O gradiente do ceu deve ser feito em **faixas horizontais discretas**, cada
  faixa de cor chapada. Conte-as e diga quantas sao. Mire em 10-14 faixas.
  (Motivo tecnico: cada faixa e uma troca de cor por interrupcao horizontal.)
- Cada camada deve ser distinguivel da vizinha por **valor** (claro/escuro),
  nao so por matiz. Se converter para preto e branco, as 5 camadas ainda
  precisam se separar.
- Camada 2 nitidamente mais dessaturada e mais clara que a camada 3.
  Perspectiva atmosferica e a ferramenta principal.
- Deixe uma faixa horizontal de ~40 px na base livre de detalhe importante —
  ali fica o HUD.
- Sem personagens nesta imagem.

**O que sera julgado:** as 5 camadas se separam em escala de cinza? O ceu tem
faixas contaveis? Da para acreditar que isso roda a 60 fps?

---

### R1-03 — Whispy Woods, boss articulado `concept_art`

**Canvas:** 1024 x 1024, fundo magenta
**Cores:** maximo 15 + transparencia

Uma arvore gigante com rosto, boss de fim de fase. Grande, imponente, mas
**bonachona** — ameacadora do jeito que um brinquedo e ameacador.

**Critico:** desenhe-a como **pecas separaveis**, porque no jogo ela e montada
com sprites articulados. Entregue:

1. A arvore montada, completa, vista de frente
2. **Ao lado, as pecas desmontadas e rotuladas:**
   - tronco (peca unica, estatica)
   - rosto: olhos, nariz bulboso, boca (pecas separadas)
   - **um galho, decomposto em 7 segmentos**, do mais grosso (base) ao mais
     fino (ponta) — este e o pedido mais importante da folha
   - maca (projetil)
   - rajada de ar (projetil, forma espiral)
3. O mesmo galho desenhado em **tres curvaturas diferentes** (reto, curvado
   para cima, chicoteando para baixo) para provar que os 7 segmentos podem
   articular sem quebrar a leitura

Aparencia: casca marrom com textura de sulcos verticais grossos, copa de
folhagem verde em massas esfericas, olhos redondos com sobrancelhas grossas
expressivas, nariz grande e arredondado.

**Restricoes duras:**
- Cada segmento de galho precisa funcionar isolado. Nada de detalhe que
  atravesse a fronteira entre segmentos.
- Segmentos devem ter no maximo 24 x 24 px na escala do jogo.
- A copa de folhagem sera feita de tiles de fundo, nao de sprite — desenhe-a
  como padrao repetivel, nao como mancha unica.
- Rosto legivel a 48 px de largura.

**O que sera julgado:** os 7 segmentos realmente encaixam nas tres curvaturas?
A copa e repetivel? O boss parece grande sem ser um borrao?

---

### R1-04 — Cinco chapeus de copy ability `concept_art`

**Canvas:** 1024 x 512, fundo magenta
**Cores:** maximo 15 + transparencia por chapeu (podem diferir entre chapeus)

Cinco chapeus/adornos que o heroi veste ao copiar um poder. **Desenhe apenas os
chapeus**, mais uma silhueta cinza-clara do heroi por baixo como guia de
posicionamento e escala.

| Poder | Chapeu | FX que o acompanha |
|---|---|---|
| FIRE | coroa/tiara flamejante | jato de chama laranja-amarelo |
| BEAM | chapeu de bruxo pontudo com estrela | arco eletrico amarelo |
| CUTTER | faixa/bandana com lamina curva | boomerang de lamina prateada |
| STONE | nenhum chapeu — o heroi vira pedra | nuvem de poeira ao aterrissar |
| SWORD | gorro verde pontudo | corte em arco branco-ciano |

Para **cada** poder, entregue tres coisas lado a lado:
1. o chapeu isolado
2. o chapeu posicionado sobre a silhueta guia
3. **o efeito visual do poder**, como forma de sprite (2-3 quadros-chave)

**Restricoes duras:**
- O chapeu nao pode ocupar mais de 20 x 12 px na escala do jogo.
- Cada poder e identificado por **cor + forma** simultaneamente. Um daltonico
  precisa distinguir FIRE de SWORD pela forma.
- STONE nao tem chapeu: entregue o heroi transformado em pedra cinza,
  mantendo a silhueta esferica reconhecivel.
- Os efeitos usarao uma faixa de paleta dedicada. Mantenha cada efeito em no
  maximo 6 cores.

**O que sera julgado:** os 5 sao distinguiveis a 28 px? A forma sozinha
identifica o poder?

---

### R1-05 — Vocabulario de terreno da Fase 1 `tileset_concept`

**Canvas:** 1024 x 1024, grade visivel de 8 px
**Cores:** maximo 15 + transparencia

Uma folha de **vocabulario de terreno**: as pecas com que uma fase inteira e
construida. Nao e uma cena — e um catalogo.

Desenhe sobre grade de 8 px claramente visivel (linhas finas cinza), rotulando
cada grupo:

1. Topo de plataforma: esquerda, meio, direita
2. Corpo/enchimento de terra: 3 variacoes para quebrar repeticao
3. Quinas internas e externas
4. Borda de plataforma flutuante (sem terra por baixo)
5. Encosta 45 graus, subindo e descendo
6. Bloco decorativo: pedra, flor, cogumelo, tufo de grama
7. Bloco destrutivel (precisa parecer quebravel a 8 px)
8. Cachoeira: 3 quadros de ciclo, tile repetivel verticalmente
9. Fundo de caverna: padrao repetivel 32 x 32

**Restricoes duras:**
- Tudo alinhado a grade de 8 px. Nada atravessando fronteira de tile sem motivo.
- O topo de grama e a terra sao tiles **diferentes**, nao um degrade continuo.
- Padroes repetiveis precisam ladrilhar sem costura visivel. Prove isso: mostre
  cada padrao repetivel ladrilhado 3x3 ao lado do tile isolado.
- Terreno solido (pisavel) precisa ser distinguivel de decoracao de fundo
  **so pelo valor**. Erro aqui vira morte injusta do jogador.

**O que sera julgado:** ladrilha sem costura? Da para montar uma fase so com
isto? Solido vs. fundo e obvio?

---

### R1-06 — Fase 2: lago e faixa submersa `palette_study`

**Canvas:** 1280 x 896, cena completa
**Cores:** maximo 45

Uma cena de lago onde a **linha d'agua corta a tela horizontalmente**.

O ponto tecnico deste pedido: no jogo, tudo abaixo da linha d'agua recebe uma
paleta diferente, trocada por interrupcao horizontal, e sofre distorcao
senoidal por linha. Preciso do plano de cor para isso.

Entregue **tres** imagens:

**(a) `concept.png`** — a cena, com a linha d'agua a ~55% da altura.

**(b) `above_below.png`** — o MESMO trecho de cenario desenhado duas vezes,
lado a lado: como aparece acima da agua, e como aparece abaixo. Mesmas formas,
paleta diferente. Abaixo: deslocado para ciano, dessaturado, mais escuro,
contraste reduzido.

**(c) `distortion.png`** — um trecho pequeno mostrando como a distorcao
senoidal por linha deforma o cenario submerso. Cada linha horizontal deslocada
lateralmente por uma onda senoidal.

**Conteudo:** agua azul-turquesa, pedras arredondadas, plantas aquaticas
ondulantes, bolhas, feixes de luz vindo da superficie, ceu com nuvens acima.

**Restricoes duras:**
- A paleta submersa precisa ser derivavel da paleta de superficie por uma
  regra simples e enunciavel. Diga qual e a regra em `notes.md`.
- A linha d'agua e uma **linha horizontal reta**, nao uma curva. Limitacao dura.
- Feixes de luz nao podem usar transparencia real. Resolva com Highlight
  (clarear) ou com padrao de dithering.

**O que sera julgado:** a regra de derivacao da paleta e simples o bastante para
virar codigo? A distorcao esta legivel?

---

### R1-07 — Tela de titulo `concept_art`

**Canvas:** 1280 x 896
**Cores:** maximo 45

Tela de titulo. Ceu noturno estrelado em gradiente indo do indigo profundo
(topo) ao rosa-lavanda (base). Estrelas espalhadas. Uma silhueta de colina com
uma arvore no primeiro plano, escura. O heroi rosa pequeno em pe na colina,
visto de costas, olhando para o ceu.

Deixe **espaco vazio deliberado** no terco superior para o logotipo (o
logotipo NAO vai nesta imagem — sera feito separadamente).

**Restricoes duras:**
- O gradiente do ceu, de novo, em faixas horizontais discretas e contaveis.
  Mire em 16-20 faixas. Conte e informe.
- A silhueta do primeiro plano em no maximo 2 cores.
- Nenhum texto na imagem.
- Estrelas em no maximo 3 tamanhos, todas alinhaveis a pixel.

**O que sera julgado:** o gradiente e contavel? Ha espaco real para o logotipo?
A imagem tem calma? A tela de titulo dita o tom do jogo inteiro.

---

## 4. COMO EU VOU JULGAR, E COMO VAI SER A RODADA 2

Cada entrega recebe um veredito por criterio:

| Criterio | Pergunta |
|---|---|
| Legalidade de cor | Todos os canais estao na grade de 8 valores? Contagem dentro do teto? |
| Legibilidade em escala | Reduzido ao tamanho real, ainda le? |
| Silhueta | Funciona em preto solido? |
| Separacao de valor | Em escala de cinza, as camadas/planos se separam? |
| Tradutibilidade | Isto vira tile de 8x8 sem virar papa? |
| Fidelidade ao tom | Doce, arredondado, com motivo de estrela? |
| Ambicao tecnica | Responde "o que o NES nao conseguiu fazer aqui"? |

O retorno vem **acionavel e quantificado**, no formato:

> "R1-02 reprovado em separacao de valor: camadas 2 e 3 tem o mesmo valor medio
> (0.62 vs 0.64) e colapsam em escala de cinza. Clareie a camada 2 em dois
> degraus e dessature 30%. Camadas 1, 4 e 5 aprovadas, nao mexa."

Nao vou dizer "ficou ruim". Se eu nao souber dizer **o que** medir, o problema
e meu, nao seu.

---

## 5. RESUMO OPERACIONAL

```
7 pedidos. Prioridade: R1-01 e R1-02 primeiro.
Saida: <projeto>/data/source_art/r1/<id>/{concept.png, prompt_used.txt, notes.md}
Cor: canais apenas em {0,36,73,109,146,182,219,255}
Teto: 15 cores (personagem) / 45 cores (cena)
PNG, nearest neighbor, chave magenta 255,0,255, sem texto, sem moldura
Em notes.md: conte as cores de verdade, e diga do que voce nao gostou
```

Se algum pedido for impossivel como escrito, **entregue o que for possivel e
diga o que nao foi** — nao invente conformidade.

---

## 6. Changelog

| Data | Mudanca |
|---|---|
| 2026-07-29 | R1 criada. 7 pedidos. Nenhuma entrega recebida ainda. |
