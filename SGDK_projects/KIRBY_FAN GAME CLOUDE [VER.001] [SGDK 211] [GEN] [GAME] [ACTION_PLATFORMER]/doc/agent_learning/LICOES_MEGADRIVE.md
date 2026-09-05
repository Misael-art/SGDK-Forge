# Licoes de Mega Drive — sintese pedagogica

> Consolidacao tematica de `failure_patterns.md` (29 entradas) e
> `success_patterns.md` (11). As tabelas sao o registro rastreavel; este
> documento e o que da para **ensinar**.
>
> Regra deste arquivo: toda licao aqui foi **medida neste projeto**, com bundle
> de evidencia citado. Nenhuma vem de tutorial ou de memoria.

---

## 1. Hardware do VDP — o que so se aprende medindo

### 1.1 Um sprite de hardware vai ate 32x32 px

Kirby de 32x32 custa **um** sprite, nao quatro. A intuicao "1 sprite por tile
8x8" faz superestimar o custo em 4x. Medido: 13 entidades = 15 sprites.

**Mas** o limite de 20 sprites **por scanline** conta sprites, nao pixels — e
existe um segundo limite de 320 px de sprite por linha. Sprite grande economiza
contagem e gasta largura.

**Consequencia de design:** uma faixa horizontal de sprites (grama de primeiro
plano) e limitada pelo teto POR SCANLINE, nao pelo de frame. Medido: 24 tufos
numa fileira deram 25/80 no frame (PASS) e 24/20 na scanline (FAIL).

### 1.2 O bit de prioridade muda de significado com Shadow/Highlight

Com S/H global ligado, o bit de prioridade deixa de ser seletor de camada e vira
seletor de brilho: tile de fundo com prioridade 0 renderiza a **meio brilho**.

Duas armadilhas medidas:

- **`VDP_clearTextArea` preenche com o glifo BRANCO da fonte**, cujo indice de
  tile e nao-zero e cuja prioridade e 0. Invisivel, mas viola o contrato. Use
  `VDP_clearPlane`.
- **O backdrop nunca pode apontar para a chave de transparencia.** A arena do
  boss saiu inteira roxa: o backdrop era magenta `(255,0,255)` e, descoberto sob
  S/H, renderiza sombreado — magenta pela metade e exatamente aquele roxo.

### 1.3 Gradiente de ceu custa UMA entrada de CRAM e ZERO tiles

Dirigindo o **backdrop** (CRAM 0) pelo H-int, o ceu inteiro sai de uma unica
entrada: onde BG_A e BG_B sao transparentes, o backdrop aparece. Dirigir um
indice de tile em vez do backdrop deixou o backdrop na chave magenta e pintou a
banda das montanhas de magenta.

### 1.4 Nao existe terceiro plano de fundo

Cinco camadas saem de dois planos: BG_B fatiado em 3 bandas por HScroll de linha,
BG_A jogavel, sprites no primeiro plano. Verificado exatamente lendo a tabela de
HScroll que a ROM programou: `cameraX=23` -> ceu 0, montanhas -2, colinas -7,
terreno -23, todos identicos a formula.

---

## 2. A licao mais cara: interrupcao no meio de uma sequencia de portas

**Sintoma:** 17 a 31 entradas contiguas de CRAM sobrescritas com um verde
uniforme, de forma **nao deterministica**. Tela verde.

**Causa:** o H-int escreve `VDP_CTRL_PORT` (endereco de CRAM) e depois
`VDP_DATA_PORT`. O SGDK faz flush da fila de DMA dentro de
`SYS_doVBlankProcess`, e um DMA tambem e "escreve a porta de controle, depois
transfere". Quando o H-int caia **entre** esses dois passos, sobrescrevia o
endereco pendente e a transferencia da tabela de HScroll aterrissava no CRAM.

**Regra geral:** *nenhuma interrupcao pode cair no meio de uma sequencia de
portas do VDP*. O H-int estava correto isolado — a vitima era o codigo
interrompido. Solucao: mascarar o H-int durante **todo** o VBlank via
`SYS_setVIntCallback`, re-armando no inicio do frame.

Corolario aplicado: toda leitura crua de VRAM no codigo do jogo roda entre
`SYS_disableInts()` / `SYS_enableInts()`.

Evidencia: 31 -> 17 -> **0** entradas corrompidas.

---

## 3. Orcamento: otimizacao vem antes de degradacao

O boss estourou o budget **duas vezes**, e as duas correcoes foram de naturezas
diferentes. A distincao e a licao.

| Ocasiao | Sintoma | Correcao | Natureza |
|---|---|---|---|
| boss sozinho | p99 87%, 2 frames estourados | interpolar as cadeias a cada 2 frames | **degradacao** (escada do §5.1) |
| boss + arena | p99 96%, 19 de 32 frames | pular rebuild de HScroll com camera estatica | **otimizacao sem perda** |

A segunda tinha **render byte-identico**: eu reconstruia 224 linhas x 2 planos
todo frame com valores iguais. Isso e desperdicio, nao custo.

**Regra:** procure desperdicio antes de gastar a escada de degradacao. Otimizacao
sem perda vem primeiro. Se muda um pixel, e degradacao disfarcada e deve ser
declarada como tal.

**Corolario:** a escada de degradacao so funciona porque foi escrita **antes** do
problema existir (ARCHITECTURE.md §5.1). Escada inventada depois do fato e
racionalizacao.

---

## 4. Medicao: o instrumento decide o que voce consegue afirmar

### 4.1 Forense de screenshot e a ferramenta errada para estado interno

Quatro metodos falharam ao medir o deslocamento do terreno: correlacao cruzada
(aliasou no padrao periodico), deteccao de borda (contagem divergiu), centroide
de cor com mascara larga (pegou faixas do ceu) e com mascara estreita (nao achou
o personagem).

A instrumentacao resolveu em uma captura. **Se o dado existe na ROM, exporte-o;
nao o reconstrua a partir de pixels.**

### 4.2 Cor de screenshot nao e cor de CRAM

O BlastEm converte 9 bits para RGB com curva de DAC realista, nao `n*255/7`.
Medido `(119,87,49)` onde a paleta tem `(109,73,36)`. **Legalidade RGB333 so pode
ser verificada no CRAM.**

### 4.3 Um gate amostrado com denominador zero e vacuo, nao aprovado

Custou uma sessao: "0 de 0 amostrados" foi lido como aprovacao. Hoje os gates
amostrados emitem aviso explicito quando o denominador e zero, e o gate de
parallax avisa quando a camera esta parada.

### 4.4 Um pico isolado de telemetria nao e custo por unidade

Suspeitei que a secao `sprite` (104 scanlines com 5 sprites) explodiria no boss.
Medi com 25 sprites: caiu para 53. Com 9: 43. **A hipotese estava errada** — e
pico ruidoso. O que escala e `cpu_load_p99`.

### 4.5 Um gate pode medir a grandeza errada

`screenshot_color_count` reprovou com 262 cores contra teto de 174 numa cena
**correta**. O teto vinha de "entradas de CRAM x 3" (S/H). Esse modelo **quebra
com raster**: o gradiente percorre UMA entrada por 12 stops no mesmo frame,
rendendo ate 36 cores sozinha.

Rebaixado a soft com o motivo escrito nele. **Enfraquecer um gate tem de ser dito
em voz alta.**

### 4.6 Gate que crasha e pior que gate que avisa

Rodar `gates.py` num bundle antigo derrubava o relatorio inteiro com `KeyError`
porque o bloco de telemetria ganhara campos novos. Bloco de telemetria e formato
**versionado**: bundles antigos ficam no disco e continuam sendo lidos. Todo
campo novo precisa de leitura tolerante que degrade para SKIP.

---

## 5. Processo — os erros que se repetiram

### 5.1 Verificar que a edicao por script APLICOU

**Duas ocorrencias na mesma sessao:**

1. Um bloco de telemetria caiu em `SCENE_stageEnter` em vez de `SCENE_stageUpdate`
   porque o alvo do `replace` casava primeiro na funcao errada.
2. Uma mudanca de passo de amostragem **nao aplicou** (a string alvo tinha
   mudado), e eu **culpei o hardware por isso** — cheguei a registrar uma licao
   dizendo que leituras de VRAM em BG_A falhavam "por motivo nao determinado".
   O diagnostico cru provou que as leituras sempre funcionaram.

**Regra:** `grep` no valor novo antes de interpretar qualquer resultado. Para
edicao estrutural, usar limites de funcao explicitos, nao `replace` com `count=1`.

### 5.2 Descartar suspeito por aritmetica antes de gastar um build

Meu primeiro suspeito pela corrupcao de CRAM foi o flash de paleta, porque era a
unica escrita nova. Escrevia **1** entrada; o defeito afetava **31**. A
aritmetica ja dizia que nao fechava. Gastei um build para descobrir o obvio.

### 5.3 Licao errada e pior que licao nenhuma

A entrada de §5.1 item 2 foi corrigida no ledger, com o erro mantido visivel. Um
registro que culpa o hardware por um bug de processo envenena todas as decisoes
seguintes.

### 5.4 Fan-out paralelo de agentes pode custar tudo

Tres subagentes Opus em paralelo morreram todos por limite de sessao sem nenhum
concluir. Serializar.

### 5.5 Nao fraudar a propria metrica

A arena do boss tem camera estatica, entao o gate de parallax passa vacuamente
ali. **Nao** adicionei drift falso para o gate ficar verde. Parallax e provado
pela cena 4.

---

## 6. Ferramental deste host (Linux)

| Fato | Detalhe |
|---|---|
| Unica rota de build | `build_sgdk_wine_bridge.sh`. `build.sh` e `new_project.sh` estao quebrados: `$GDK/bin` tem `cp -> cp.exe` e sombreia coreutils |
| `blastem.bin` acumula | Sobrevive a `flatpak kill`, nao aparece confiavelmente em `flatpak ps`, e trava a captura seguinte. Limpar por PID antes de uma serie de capturas |
| `pkill -f blastem` | **Nunca** — o padrao casa com o proprio comando do agente |
| Projeto novo | `doc/10-memory-bank.md` nasce com o historico do TEMPLATE dentro. E a autoridade #1 da hierarquia de verdade. Zerar na primeira sessao |
| Adicionar cena | 4 lugares: enum, `APP_SCENE_COUNT`, `APP_sceneName`, dispatch. Esquecer a constante nao gera erro, so um fallback mudo |

---

## 7. Contratos de arte com agente externo

- Declarar a **grade de cor legal do hardware** e a **escala real de destino**
  dentro do pedido. Resultado: 11 de 11 entregaveis com 0.00% de pixels ilegais
  na primeira rodada.
- Exigir **relatorio mecanico com numero por criterio**. O executor declarou
  espontaneamente a metrica que o reprovava e o hack que usou para atingir o alvo.
- Pedir **autocritica honesta**. O agente previu o proprio defeito antes do
  julgamento.
- **Criterio de valor em espaco indexado vai em degraus de paleta, nao em float.**
  Uma janela apertada de luminancia sobre grade discreta forcou dithering, que
  criou cores novas e estourou o teto de paleta. O criterio causou o defeito.
- **Toda metrica numerica precisa vir com a FORMULA.** Diretor e executor usavam
  formulas de luminancia diferentes e chegavam a numeros diferentes para a mesma
  imagem. Passou por sorte.
- **Parar o loop quando os defeitos passam a ser dos criterios, nao do trabalho.**
  Aconteceu por 3 rodadas seguidas.

---

## 8. Changelog

| Data | Mudanca |
|---|---|
| 2026-08-06 | v1. Sintese de 40 entradas do ledger em 7 temas. Escrito porque uma tabela de 29 linhas registra mas nao ensina. |
