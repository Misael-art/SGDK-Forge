# CHANGES.md — Registro por sessao

> Exigido pela regra dura 6 do brief: toda sessao termina aqui, com melhorias,
> score do critico por subsistema e custo acumulado.

---

## Sessao 001 — 2026-07-29 — FASE 0 (parcial) + FASE 3 (parcial)

**Encerramento:** involuntario. Limite de sessao da API atingido (reset 16:50
America/Sao_Paulo). Tres subagentes morreram no meio do trabalho. Isso esta
registrado como fato, nao como falha de engenharia.

### O que realmente existe agora

| Entregavel | Status | Evidencia |
|---|---|---|
| Projeto criado e nomeado no padrao canonico | feito | `validate_project_name` = valid |
| Contexto classificado `aaa_game` | feito | `validate_project_context` = `status=ok blockers=0` |
| Rota de build em Linux | **verificada** | `wine_bridge_status=buildado`, `out/rom.bin` 262144 B |
| Rota de captura BlastEm em Linux | **verificada** | bundle `status: sealed blockers: []` |
| `doc/ARCHITECTURE.md` | feito | 418+ linhas, com primeira medicao real |
| Probe VLAB portado e ligado | **verificado** | 2 bundles selados com `vdp_dump` + `runtime_metrics` |
| `tools/harness/gates.py` | feito e rodando | `gate_report.json` com 13 gates |
| `tools/harness/frametime.py` | escrito | nao exercitado end-to-end |
| `tools/harness/probe_format.py` | escrito | usado por gates.py |
| `doc/art/AI_IMAGE_PROMPT_PACK.md` + manifesto | feito | 7 pedidos R1, diretorios criados |
| `doc/VRAMMAP.md` | **NAO EXISTE** | agente morreu antes de escrever |
| `doc/PALETTES.md` | **NAO EXISTE** | idem |
| `doc/SOUNDMAP.md` | **NAO EXISTE** | agente morreu ainda lendo prior art |
| `doc/17-audio-design.md` | stub do template | nao tocado |
| `tools/harness/build_and_capture.sh` | **NAO EXISTE** | agente morreu antes |
| `tools/harness/imagediff.py` | **NAO EXISTE** | idem |
| `tools/harness/README.md` | **NAO EXISTE** | idem |
| Playtest scriptado | **NAO EXISTE** | nao iniciado |
| Codigo de jogo (Kirby, fases, boss) | **ZERO** | FASE 1 nao comecou |

### Score do critico por subsistema

**Nao ha score nesta sessao, e nao deveria haver.** A FASE 2 (gauntlet
construtor/critico) exige capturas de subsistemas implementados. Nao existe
subsistema de jogo implementado. Dar score agora seria inventar numero.

O que existe e a **linha de base do instrumento**, medida na ROM do template:

| Subsistema | Estado | Medicao |
|---|---|---|
| Instrumentacao | operacional | 13 gates, 2 bundles selados |
| Cores | baseline | 21/61 simultaneas, 0 ilegais em RGB333 |
| Sprites | vazio | 0/80, 0/20 — nada a medir ainda |
| VRAM | baseline | tabelas em range e disjuntas; budget de tile em `warn` (falta VRAMMAP.md) |
| Performance | baseline | p99 = 42/100, 0 frames acima do budget, 171 scanlines de folga |
| Parallax / Raster / Audio / Boss / Game feel | nao implementado | — |

### Descobertas que mudam o plano

1. **`tools/sgdk_wrapper/build.sh` e `new_project.sh` estao quebrados neste host
   Linux.** Causa raiz: `env.sh` prepende `$GDK/bin` ao PATH e esse diretorio
   contem symlinks `cp -> cp.exe`, `mkdir -> mkdir.exe`, `rm -> rm.exe`. O
   coreutils POSIX e sombreado por binarios Windows sob Wine que nao entendem
   caminho `/mnt/...`. Unica rota funcional: `build_sgdk_wine_bridge.sh`.
   **Nao corrigido de proposito** — `tools/sgdk_wrapper/` e canonico e exige
   aprovacao humana explicita (AGENTS.md).

2. **Graphify nao fica `fresh` neste host**, mesma classe de bug de caminho
   (`graphify_forge.ps1:53`). Logo `assert_agent_environment.ps1` retorna
   `blocked reason=prepare_failed`. Graphify e indice consultivo e nunca fonte
   de verdade, entao nao bloqueia producao — mas o guard verde nao e alcancavel
   neste host hoje.

3. **A folga real de CPU e mensuravel e e generosa na cena vazia:** 171
   scanlines de `vblank_idle`. Mas 90 scanlines vao para desenhar texto na
   `scene_demo` — o custo de `VDP_drawText` e alto e vai sair do jogo final.

4. **O risco dominante do projeto e arte, nao codigo** (ARCHITECTURE.md §10,
   risco A5). Por isso o pacote de imagens R1 foi priorizado e entregue nesta
   sessao mesmo com a FASE 0 incompleta.

### Custo acumulado

| Recurso | Valor |
|---|---|
| Sessoes | 1 |
| Limite de API | atingido uma vez (3 subagentes perdidos) |
| Subagentes lancados | 3 (harness, vram+paletas, audio) |
| Subagentes que concluiram | 0 — harness chegou a ~80%, os outros a ~0% |
| Builds executados | 2 (1 falho por rota errada, 1 ok) |
| Bundles BlastEm selados | 2 |

Licao operacional: **lancar 3 subagentes Opus em paralelo esgotou o orcamento
da sessao antes de qualquer um terminar.** Na proxima sessao, serializar: um
subagente por vez, ou fazer os documentos localmente. Registrado tambem em
`doc/agent_learning/`.

### Proxima sessao — ordem exata de retomada

1. `doc/VRAMMAP.md` — desbloqueia o gate `vram_tile_budget`, que hoje esta `warn`
2. `doc/PALETTES.md` — decisao de Shadow/Highlight **antes** de qualquer arte final
3. `tools/harness/build_and_capture.sh` + `imagediff.py` + README
4. `doc/SOUNDMAP.md` + `doc/17-audio-design.md`
5. Julgar as entregas R1 do Codex, se existirem (`data/source_art/r1/`)
6. So entao FASE 1: Kirby jogavel com parallax de 5 camadas

**Nao comecar a FASE 1 antes de 1 e 2.** Escrever codigo de cenario sem mapa de
VRAM e sem contrato de paleta e exatamente o erro que os gates existem para
impedir.

---

## Sessao 002 — 2026-07-30 — FASE 1 (nucleo: Kirby jogavel + 5 camadas)

### O que roda, com evidencia

| Item | Estado | Evidencia |
|---|---|---|
| Kirby controlavel (correr/pular/flutuar) | `testado_em_emulador` | bundle `fase1_parallax_w12` selado |
| 5 camadas de parallax de 2 planos | `testado_em_emulador` | screenshot + medicao de deslocamento |
| Gradiente de ceu por H-int | `testado_em_emulador` | 12 faixas visiveis na captura |
| Shadow/Highlight global ligado | `implementado` | nao verificavel: probe nao exporta o registro |
| Todos os gates | **PASS, 0 warnings** | `gate_report.json` |

Numeros medidos na cena STAGE (`scene_id=4`, frame 1080):

```
cores simultaneas    40 / 58
CRAM ilegal           0
cores no screenshot 152 / 174   (teto ja considera o x3 do S/H)
sprites/frame         5 / 80
sprites/scanline      4 / 20
frames > budget       0 / 0
cpu p99              39 / 100

atribuicao por secao, scanlines/frame:
  input 2 | scene 55 | audio 1 | sprite 104 | vblank_idle 226
```

### Parallax: o que esta PROVADO e o que nao esta

Duas capturas em pontos diferentes do pan de abertura, deslocamento medido por
correlacao cruzada por banda:

```
camada 2 montanhas (projeto: camX/8)      -15 px MD
camada 3 colinas   (projeto: camX*11/32)  -40 px MD
razao medida 15:40 = 1:2.67
razao de projeto 3/8 = 1:2.67             CONFERE
```

**Isso prova que as camadas se movem em velocidades diferentes e na proporcao
projetada.** E a prova central da FASE 1.

**Nao provado:** o deslocamento da camada 4 (terreno). A correlacao devolveu
+42 px, que e inconsistente com a camera inferida das camadas 2 e 3 (~118 px).
Causa: o padrao xadrez do terreno e periodico e a correlacao aliasa. Tentei medir
pela borda dos vaos, que e feicao unica, e o detector de limiar falhou. **Fica
como medicao devida, nao como numero.** O terreno usa literalmente `-cameraX`,
entao o valor correto e o proprio deslocamento da camera, mas isso e argumento de
codigo, nao medicao.

### Dois achados de runtime

1. **O gradiente de ceu deve dirigir o BACKDROP (CRAM 0), nao um indice de tile.**
   Descoberto rodando: dirigindo o indice 1, o backdrop ficava na chave magenta e
   a faixa das montanhas saia magenta na tela. Com o backdrop, o ceu inteiro custa
   **1 entrada de CRAM e ZERO tiles** — melhor que o previsto em PALETTES.md §4.1.
   `inc/systems/raster.h` registra a descoberta no comentario.

2. **`sprite` = 104 scanlines/frame para apenas 5 sprites.** E a maior fatia de
   custo da cena e parece alto demais. Nao investigado. **Registrado como suspeita
   medida, nao explicada.**

### Correcoes de API

- `fix16ToInt` esta **deprecado** no SGDK 2.11 e o compilador o rejeita com erro,
  nao warning. Substituido por `F16_toInt` em todo o codigo novo.

### O que NAO foi entregue da FASE 1

A FASE 1 do brief pede `titulo -> fase 1 -> boss -> game over/continue`. Entreguei
o **nucleo** dela, nao ela inteira:

- sem tela de titulo propria (o menu do template segue no lugar)
- sem inimigos, sem inalar, sem copy abilities
- sem boss
- sem game over / continue
- sem audio (SOUNDMAP escrito, zero nota toca)
- sem playtest scriptado (nenhum input automatizado existe)
- `INTRO_PAN_FRAMES = 900` e **PROVISORIO**: foi esticado para a captura cair
  dentro do pan. Valor de producao nao decidido.
- divida do template nos gates de audio segue em baseline (11 violacoes)

### Custo acumulado

| Recurso | Valor |
|---|---|
| Sessoes | 2 |
| Builds | 8 (2 falhos: rota errada, `fix16ToInt` deprecado) |
| Bundles BlastEm selados | 7 |
| Gates ativos | 14 runtime + 5 audio estaticos |

---

## Sessao 003 — 2026-07-30 — Inimigos, inalar, e um bug grave de CRAM

### As duas investigacoes que eu recomendei, e o que elas deram

**1. Secao `sprite` = 104 scanlines: minha hipotese estava ERRADA.**

| sprites | secao `sprite` | cpu p99 |
|---|---|---|
| 5 | 104 | 39% |
| 25 | **53** | 60% |
| 9 | 43 | 43% |

O custo **caiu** ao adicionar sprites. A secao e pico ruidoso e nao escala com
contagem. Nao havia nada a otimizar. O que escala de verdade e `cpu_load_p99`.

**Achado novo e util do mesmo teste:** 24 tufos numa unica fileira horizontal
passaram `sprites_per_frame` (25/80) e **falharam** `sprites_per_scanline`
(24/20). Para uma faixa horizontal de sprites o limite que morde e o por
scanline. Cota da camada 5 voltou aos 8 documentados, agora com o motivo medido
escrito no codigo.

**2. Deslocamento da camada 4: nao consegui medir, e a ferramenta esta errada.**
Quatro metodos de forense de screenshot falharam. A conclusao honesta e que
screenshot e ambiguo demais (padrao periodico, cores parecidas, curva de DAC do
emulador). A medicao exata exige `cameraX` no bloco VLAB. Fica devido.

Descoberta lateral que muda um gate: **as cores do screenshot nao estao na grade
RGB333** — o BlastEm usa curva de DAC realista. Legalidade de cor so pode ser
verificada no CRAM, nunca no PNG.

### O que passou a existir

- `src/entities/enemy.c`: pool FIXO de 6, IA que vira em beirada e borda
- **Inalar**: cone de 72 px a frente do Kirby, inimigo puxado, engolido a 12 px,
  e o engolir **concede a copy ability**. Inalar enraiza o Kirby de proposito
- Botoes: **A = pular/flutuar, B = inalar.** C e proibido para gameplay (o
  template o usa para o toggle de HUD)

### Dois bugs, um deles grave

**Bug 1: o pan de abertura congelava a simulacao inteira.** Kirby e os inimigos
flutuavam no ar porque a gravidade nunca rodava. Corrigido: o pan suprime apenas
o INPUT. Um pan sobre mundo vivo le como intencional; sobre mundo congelado le
como bug de fisica.

**Bug 2, grave: corrupcao NAO DETERMINISTICA de 17 a 31 entradas contiguas de
CRAM.** A tela ficava verde. Diagnosticado lendo os dumps de CRAM, nao por
palpite:

> O H-int escreve `VDP_CTRL_PORT` (endereco de CRAM) e depois `VDP_DATA_PORT`.
> O SGDK faz flush da fila de DMA dentro de `SYS_doVBlankProcess`, e um DMA
> tambem e "escreve a porta de controle, depois transfere". Quando o H-int caia
> **entre** esses dois passos, sobrescrevia o endereco pendente e a transferencia
> da tabela de HScroll aterrissava no CRAM.

O H-int estava correto isolado — a vitima era o codigo interrompido. Corrigido
mascarando o H-int durante **todo** o VBlank via `SYS_setVIntCallback`, re-armando
em `RASTER_frameStart`. **Verificado: 31 -> 17 -> 0 entradas corrompidas.**

Meu primeiro suspeito (o flash de paleta) foi **refutado** desligando-o: a
corrupcao persistiu. A aritmetica ja dizia que nao fechava — 1 entrada escrita
contra 31 corrompidas. Licao registrada.

### Gates finais

```
14 gates de runtime   PASS, 0 warnings
 5 gates de audio     PASS
40/58 cores | 0 CRAM ilegal | 166/174 cores de screenshot
15/80 sprites por frame | 8/20 por scanline
0 frames acima do budget | cpu p99 51/100
```

### O que continua faltando

titulo proprio, as outras 4 copy abilities (so FIRE existe, e sem moveset),
boss, game over/continue, audio tocando, playtest scriptado, `INTRO_PAN_FRAMES`
em 900 provisorio, e a instrumentacao do probe (`cameraX`, S/H, prioridade, DMA).

---

## Sessao 004 — 2026-07-30 — Instrumentacao do probe

### Por que um bloco novo em vez de estender o VLAB

O selador canonico `seal_fresh_evidence_bundle.py` le o VLAB como "words[0..23]
sao metricas, words[24..] sao as 64 entradas de CRAM". Acrescentar metrica ao
VLAB deslocaria a paleta e **corromperia silenciosamente todos os gates de cor do
workspace**. Esse selador e ferramenta canonica compartilhada e AGENTS.md proibe
alterar sem aprovacao humana. Entao o projeto passou a emitir o proprio bloco
**`KRB1` em SRAM 0x300**, com leitor proprio em `tools/harness/`.

### O ganho principal: parallax verificado EXATAMENTE

O que 4 metodos de forense de screenshot nao conseguiram, a leitura direta
resolveu em uma captura:

```
cameraX = 23
camada 1 ceu        hscroll     0   esperado     0   OK
camada 2 montanhas  hscroll    -2   esperado    -2   OK
camada 3 colinas    hscroll    -7   esperado    -7   OK
camada 4 terreno    hscroll   -23   esperado   -23   OK
```

**As quatro camadas conferem com a formula de projeto, incluindo o terreno**, que
era a medicao que ficou devendo na sessao 003. Divida quitada.

### Orcamento de DMA: agora medido, nao planilha

```
dma_peak_bytes = 1792 B/frame
limite do projeto (SOUNDMAP §5.2) = 4096 B
teto de hardware NTSC (dma.h:172)  = 7372 B
```

O orcamento de `doc/VRAMMAP.md` §3.1 estimava 3176 B com a tabela de HScroll de
896 B como item obrigatorio. O medido e 1792 B, ou seja **abaixo da estimativa**.
A folga e real.

### Um bug encontrado pela propria instrumentacao

`prio_viol_BGA = 16 de 16 amostrados` no primeiro run. Causa: `VDP_clearTextArea`
preenche a area com o glifo BRANCO da fonte, cujo indice de tile e nao-zero e
cuja prioridade e 0. Invisiveis, mas com S/H global sao exatamente o que o gate
P5 proibe. Trocado por `VDP_clearPlane`: **16/16 -> 0**.

### O que NAO ficou provado, e nao vou dizer que ficou

- ~~**Gate P5 esta PARCIAL, nao aprovado.**~~ **CORRIGIDO AINDA NESTA SESSAO.**
  Eu havia escrito que as leituras de VRAM em BG_A retornavam zero "por motivo
  nao determinado", levantando suspeita de delay de leitura ou restricao em
  display ativo. **Essa afirmacao estava errada.** Diagnostico cru provou que as
  leituras sempre funcionaram: BG_A linha 22 col 0 devolve `0xA083`
  (tile 131, prioridade 1, paleta 1). A causa real foi um `str.replace` meu que
  **nao aplicou** — o passo de amostragem continuou em 128 bytes, cobrindo so as
  linhas 0-15, onde BG_A esta vazio. Eu acreditei que a edicao tinha aplicado e
  culpei o hardware. Com o passo corrigido para 256 bytes:
  **P5 = 0 violacoes de 17 amostrados (BG_A 4, BG_B 13), nao vacuo, PASS.**
- **`sh_enabled` prova INTENCAO, nao hardware.** SGDK 2.11 nao expoe leitura do
  registro 0x0C, entao o valor e uma copia-sombra do que a ROM pediu.
- Gate A5 (`missed_frames` do XGM2) continua ausente: nao ha audio tocando.

### Gates

**18 gates de runtime PASS, 0 warnings.** 5 de audio PASS. cpu p99 58/100.

Quatro gates novos, todos possiveis so por causa do bloco KRB1:
`parallax_layer_speeds`, `tile_priority_under_sh`, `dma_peak_per_frame`,
`shadow_highlight_intent` (soft, e rotulado como intencao).

Escrito tambem `tools/harness/README.md`, que o header do `gates.py` ja mandava
ler desde a sessao 001 mas que nunca existiu — o agente do harness morreu antes.
Ele separa explicitamente os gates que PODEM falhar dos que sao invariantes
estruturais e nao podem, para que um run verde nao seja lido como mais prova do
que e.

---

## Sessao 005 — 2026-08-06 — Playtest scriptado + boss Whispy Woods

### Playtest: o loop central agora esta PROVADO, nao suposto

Input gravado **do lado da ROM** (`src/system/playtest.c`), nao injecao de teclas
no emulador. Motivo: determinismo. Injecao via xdotool depende de foco de janela,
timing do X11 e polling do emulador, e o mesmo script daria frames diferentes a
cada execucao — o gate seria instavel. Uma tabela compilada e frame-exata.

Roda na **cena 5** (`APP_SCENE_STAGE_PLAYTEST`), separada da cena 4 jogavel, para
nao vazar para o jogo normal. Cena separada porque o bloco de bootstrap canonico
carrega apenas um scene id, sem campo de flags, e e escrito por ferramenta
compartilhada que este projeto nao pode alterar.

```
playtest: step=17  finished=1  visited=0x07FF
cobertura: 11/11 estados   faltando: nenhum
```

**`swallow` e `ability` deram SIM, e `enemies_alive` caiu de 4 para 2.** Essa e a
prova que faltava: inalar, engolir e conceder copy ability **funcionam na ROM**,
nao apenas compilam. Dois gates novos: `playtest_coverage` e `playtest_completed`.

Detalhe importante: cada bit e marcado pela **cena observando o estado acontecer**,
nao pelo script pedindo. Cobertura ALCANCADA, nao cobertura pretendida.

### Boss Whispy Woods: implementado, e ele reprovou o gate

4 galhos x 7 segmentos com cinematica direta e `F16_sin`/`F16_cos` em graus.
Zero float. Tronco em tiles de BG_A, custo zero de sprite.

Medido: **39 sprites de hardware por frame** (28 segmentos + 8 macas + rosto +
Kirby), 10 por scanline, 39/58 cores.

Mas a primeira captura **FALHOU** `zero_over_budget_frames`:

```
cpu p99                87%
frames acima do budget  2      <-- FAIL
```

Isso e o **risco A3 do ARCHITECTURE.md §10 se materializando**, com a
probabilidade "media" que eu tinha estimado.

### A escada de degradacao funcionou como escrita

Apliquei a **alavanca 1 exatamente como o §5.1 previa** — interpolar a cada 2
frames em vez de todo frame:

| | antes | depois |
|---|---|---|
| cpu p99 | 87% | **75%** |
| frames acima do budget | **2** | **0** |
| pico da secao `sprite` | 148 | 114 |
| veredito | **FAIL** | **PASS** |

Restam as alavancas 2 (5 segmentos por galho) e 3 (3 galhos). O rosto nunca e
cortado. Isso so funcionou porque a escada foi escrita **antes** de existir o
problema; escada inventada depois do fato e racionalizacao.

### Dois bugs

1. **Backdrop apontando para a chave de transparencia.** A arena inteira saiu roxa:
   o backdrop era o magenta `(255,0,255)` e, com S/H global e sem tile de
   prioridade cobrindo, o backdrop renderiza SOMBREADO — magenta pela metade e
   exatamente aquele roxo. Corrigido com `PAL_setColor(0, ...)` para uma cor real.
2. **`window_timeout` na captura** com `blastem.log` de 0 bytes. Matei o
   `blastem.bin` orfao por PID e **nao resolveu**: o bloqueio era uma instancia
   **flatpak** presa, visivel em `flatpak ps` e nao em `ps`. Ela se liberou sozinha
   e a tentativa seguinte passou. `tools/harness/README.md` corrigido — a
   instrucao anterior mandava olhar so `ps` e estava incompleta.

### O que este boss AINDA nao e

- sem dano por contato: ele perde HP num timer, so para medir o pior caso
- sem arena: fundo e cor chapada, sem as 4 camadas
- `tile_priority_under_sh` ficou **vacuo** nesta cena (0 amostradas): o tronco
  esta nas colunas 16-23 e a amostragem le so a coluna 0. O gate reportou isso
  corretamente em vez de dar PASS silencioso
- sem derrota jogavel, sem transicao, sem audio

---

## Sessao 006 — 2026-08-06 — Arena do boss com as 4 camadas

### A previsao estava certa, e pior do que eu esperava

Eu havia dito que os 75% do boss foram medidos com fundo chapado e que somar
parallax + raster era onde o orcamento podia estourar. Somei:

| | boss chapado | boss + arena |
|---|---|---|
| cpu p99 | 75% | **96%** |
| frames acima do budget | 0 | **19 de 32** |

19 de 32 frames amostrados estourando nao e marginal, e falha.

### Procurei DESPERDICIO antes de gastar a escada de degradacao

A camera da arena e **estatica**, e eu reconstruia a tabela de HScroll de 224
linhas x 2 planos **todo frame com valores identicos** — CPU para calcular e
banda de DMA para re-enviar os mesmos bytes.

Pular o rebuild quando a camera nao move:

| | antes | depois |
|---|---|---|
| cpu p99 | 96% | **78%** |
| frames acima do budget | 19 | **0** |
| pico de DMA | 1792 B | **896 B** |

**Resultado renderizado byte-identico.** Por isso essa era a correcao certa a
gastar antes da alavanca 2 do boss: otimizacao sem perda vem antes de degradacao.
Se mudasse um pixel, seria degradacao disfarcada.

A alavanca 2 (5 segmentos por galho) e a 3 (3 galhos) seguem **sem uso**.

### Tres bugs, e um deles no meu proprio gate

1. **`sh_enabled=0` na arena.** `PROBE_STAGE_reset()` zera todos os campos
   publicados e rodava DEPOIS do publish do S/H, apagando-o em silencio. O gate
   pegou — o que confirma que vale ter telemetria de INTENCAO mesmo sem poder ler
   o registro do hardware.

2. **O gate `screenshot_color_count` estava medindo a grandeza errada.**
   Reprovou com 262 cores contra teto de 174 numa cena **correta**. O teto vinha
   de "entradas de CRAM uteis x 3" (normal/sombra/highlight). Esse modelo
   **quebra com raster**: o gradiente de ceu percorre UMA entrada de CRAM por 12
   stops dentro do mesmo frame, rendendo ate 36 cores de tela sozinha.
   Rebaixado a SOFT, com o motivo escrito dentro do proprio gate. A restricao
   real e ocupacao de CRAM, que `color_budget` ja cobra contra o limite de 58
   (mediu 38). **Enfraquecer um gate tem de ser dito em voz alta.**

3. **Processos de captura acumulando.** Cinco capturas seguidas falharam com
   `window_timeout`. `flatpak ps` vazio, `flatpak kill` nao matou nada, e mesmo
   assim varios `blastem.bin` vivos em `ps`. Eles sobrevivem ao `flatpak kill` e
   se acumulam a cada falha. A limpeza por PID resolveu. README corrigido — a
   instrucao anterior, escrita ha duas sessoes, estava incompleta e a desta
   sessao tambem estava (eu tinha culpado a instancia flatpak).

### Estado da arena

Gradiente de ceu por H-int, montanhas, colinas, terreno e o boss articulado, tudo
dentro do orcamento: **cpu p99 78%, 0 frames estourados, DMA 896 B de 4096,
38/58 cores, 39 sprites/frame, 13 entradas de prioridade amostradas sem violacao.**

Aviso honesto que o proprio harness emite: `parallax_camera_moved` avisa que a
arena tem camera estatica e portanto o gate de parallax passa VACUAMENTE ali.
Nao adicionei drift falso so para o gate parecer verde — isso seria fraudar a
propria metrica. Parallax e provado pela captura da cena 4.

---

## Sessao 007 — 2026-08-06 — Dano por contato, derrota, e a sintese pedagogica

### Registro pedagogico consolidado

`doc/agent_learning/LICOES_MEGADRIVE.md`: sintese tematica das 40 entradas do
ledger em 7 temas. Escrito porque uma tabela de 29 linhas **registra mas nao
ensina**. Duas lacunas do ledger tambem foram preenchidas:

- adicionar cena exige mexer em **4 lugares**, e esquecer `APP_SCENE_COUNT` nao
  gera erro de compilacao — so um fallback mudo para a cena default
- **um sprite de hardware vai ate 32x32 px**: Kirby custa UM sprite, nao quatro.
  A intuicao "1 sprite por tile" superestima o custo em 4x

### O loop de combate esta PROVADO

Kirby ganhou vida (6), i-frames (60 frames com blink) e knockback com o arco do
§7 (`vy -2.5`, gravidade `0.25`, tudo em `fix16`).

O contra-ataque e **o verbo do Kirby, nao uma espada**: Whispy joga macas, o
jogador inala a maca e a devolve como dano. Os galhos so machucam **nas duas
pontas e so durante `BOSS_WHIP`** — galho que fere parado seria ilegivel.

Medido no playtest scriptado da cena 7:

```
playtest_boss_combat: 3/3 estados alcancados
  kirby_hurt  SIM      boss_hurt  SIM      boss_dead  SIM
boss hp = 0    kirby health = 4/6    boss derrotado = SIM
```

**Isso fecha o primeiro loop completo do jogo em evidencia**, nao em intencao.

### Tres erros meus, todos no gate ou no script

1. **Script bom de jogar e ruim de cobrir.** Segurando B do inicio ao fim, Kirby
   engolia toda maca antes de ser atingido e `kirby_hurt` ficava NAO — o caminho
   de dano nele nunca era exercitado. Corrigido inserindo 300 frames parado sem
   inalar: **tomar dano de proposito**.
2. **Script mais longo que a captura.** 2400 frames sob captura de 32 s parou no
   passo 6 de 7. Encurtado para ~1610 frames. O gate `playtest_completed` existe
   exatamente para pegar isso.
3. **Gate exigindo o que a cena nunca prometeu.** `playtest_coverage` reprovou a
   captura de boss por faltar 8 dos 11 estados de locomocao — que sao trabalho do
   script de FASE. Agora o gate detecta captura de boss pelos bits de combate e
   reporta locomocao como informativo. **Um gate que reprova a cena por algo que
   ela nunca prometeu treina o time a ignorar gates.**

### Numeros da arena com combate

```
39 sprites/frame | 11/scanline | cpu p99 90/100 | 0 frames acima do budget
```

O p99 subiu de 78% para 90% com a colisao AABB ativa. Continua dentro, mas a
margem encolheu, e as alavancas 2 e 3 da escada seguem sem uso.

---

## Sessao 008 — 2026-08-06 — Game over, continue, e o loop da FASE 1 fechado

### O criterio literal da FASE 1 esta cumprido

O brief pede: **titulo -> fase 1 -> boss -> game over/continue**. O que existe
agora, com evidencia por cena:

| Cena | id | Estado |
|---|---|---|
| STAGE (fase jogavel) | 4 | `testado_em_emulador` |
| STAGE_PLAYTEST | 5 | 11/11 estados cobertos |
| BOSS + arena de 4 camadas | 6 | `testado_em_emulador` |
| BOSS_PLAYTEST | 7 | 3/3 do loop de combate |
| GAMEOVER / vitoria + continue | 8 | `testado_em_emulador` |

Falta **titulo proprio** — hoje o branding do template ocupa esse lugar.

### O que passou a existir

- **Dano de inimigo na fase**, com uma regra de design: inimigo sendo INALADO nao
  machuca. O vortex nao pode punir o jogador por usar o verbo central.
- **Tela de game over/vitoria com continue**: countdown de 9 s, `START`/`A` para
  continuar, e trava de 45 frames antes de aceitar input — o botao que te matou
  nao pode queimar o prompt no mesmo movimento.
- **Transicoes**: derrota na fase e na arena -> game over; boss derrotado ->
  vitoria. As cenas de playtest **nao** transicionam, senao a captura sairia da
  arena antes de amostrar os estados de combate.

### O gate semantico canonico me reprovou, e estava certo

A primeira versao da tela era cor chapada com texto. O selador rejeitou o bundle
com `blank_or_low_information_capture`.

**Nao contestei o gate.** Para um alvo AAA, uma tela de game over que e um vazio
e uma reclamacao legitima, nao falso positivo. Refiz: o vale continua visivel
atras da mensagem, com o gradiente de ceu por raster mudando de humor (quente na
vitoria, frio na derrota). Passou — e a tela ficou melhor, nao so aprovada.

Decisao tecnica associada: **S/H desligado nesta cena**. Os tiles de fonte do
SGDK sao escritos em prioridade 0, e sob S/H global todos renderizariam a meio
brilho. `doc/PALETTES.md` §2.2 trava S/H para cenas de gameplay por causa do
vortex; uma tela de texto nao tem essa necessidade.

### Regressao

```
stage_regress (cena 4)   PASS   parallax 4/4 exato, cpu p99 50%
gameover2     (cena 8)   PASS   cpu p99 15%
```

O parallax voltou a ser medido com camera em movimento (`camera_x=47`):
ceu 0, montanhas -5, colinas -16, terreno -47 — **todos exatos**.

### Defeito visual aberto

Ha uma coluna pontilhada fina no ceu da tela de game over (aprox. x=215,
linhas 2-7). Nao vem do texto, que e desenhado nas linhas 10-17. Nao investiguei.
Fica registrado como defeito aberto em vez de ignorado.

---

## Sessao 009 — 2026-08-06 — Audio: router, musica tocando e um erro meu de instrumento

### O medo nao se confirmou: audio custa ~0 de CPU do 68000

Eu havia dito que o audio era o que mais podia mexer no orcamento, ja em 90% na
arena. Medido:

| | sem audio | com audio |
|---|---|---|
| cpu p99 (fase) | 50% | **50%** |
| secao `audio` | 1 | **2 scanlines** |
| pico de DMA | 896 B | **896 B** |

**Custa quase nada, e isso e o XGM2 fazendo exatamente o que promete**: o mixing
roda no Z80, nao no 68000. A preocupacao era legitima mas a arquitetura escolhida
em `doc/SOUNDMAP.md` §1 ja resolvia. Vale registrar que a decisao de driver, que
parecia so uma escolha de ducking, tambem comprou isso.

### O que existe

- `src/audio/xgm_router.c` — o dono unico previsto no contrato. 8 faixas de
  prioridade, janela de supressao de 4 frames por sample, fila de UM slot para
  prioridade >= 11, ducking (50% por 12 frames em dano, 75% por 8 no verbo do
  jogador, nada abaixo de 9 para a musica nao pulsar).
- `data/builders/build_placeholder_audio.py` — gera um **VGM real** (header 1.50,
  stream 0x52/0x53/0x50/0x62/0x66) com baixo FM, lead FM e PSG dobrando, mais 3
  samples PCM. **Nao e a trilha composta**; existe para exercitar o pipeline e
  permitir a medicao acima antes de alguem escrever uma nota.

### Um erro meu, e ele quase virou "correcao" de um problema inexistente

Li `audio.raw` do BlastEm como int16 e conclui que a musica era uma onda quadrada
em escala cheia: pico -0.1 dBFS, RMS -5.7 dBFS. **Tudo errado.** O arquivo e
**float32, 48 kHz, estereo**, e o pico real era **-18.5 dBFS**.

O que expos o erro foi um teste de controle: desliguei a musica e o RMS **subiu**
(27550 sem musica contra 16906 com). Resultado fisicamente impossivel. Quando um
controle devolve absurdo, **o instrumento esta errado, nao o sistema**.

Pior: eu ja tinha mudado codigo com base na leitura errada (silenciar PSG, subir
TL). Mantive as mudancas porque sao corretas em si — o PSG realmente liga em
atenuacao 0 — mas corrigi o comentario para **nao reivindicar** ter consertado
algo que nunca existiu.

A informacao estava a um `grep` de distancia, no `blastem.log` do proprio bundle:
`Initialized audio at frequency 48000 ... 32-bit float format`.

### Dois gates novos, e um antigo corrigido

- **A8 `music_audible`**: RMS 0.0340 contra piso de silencio 0.015 **medido**
  (nao chutado) com a musica desligada. Prova que sai som. Diz explicitamente que
  nao julga se a musica e boa — isso e checklist humano.
- **A9 `dac_headroom`**: pico 0.1186 contra teto 0.85, entao PCM simultaneo nao
  clipa a mistura.
- **Baseline de audio corrigida.** A condicao de expiracao dizia "quando
  `xgm_router.c` existir". Ele existe e a divida **continua**, porque as 11
  violacoes estao nas cenas do TEMPLATE, ainda ligadas em `app.c`. Uma condicao
  cumprida com a divida viva le como "resolvido" — pior que nao ter condicao. O
  warning agora **le a condicao do proprio arquivo** em vez de repeti-la no codigo.

### Estado

```
fase (cena 4)  parallax 4/4 EXATO, cpu p99 50%, 0 frames estourados
audio          A8 + A9 PASS, 5 gates estaticos PASS, 2 warnings de divida herdada
PCM em ROM     8.9 KB de 384 KB
```

---

## Sessao 010 — 2026-08-06 — Tela de titulo: a FASE 1 fecha

### O criterio literal da FASE 1 esta COMPLETO

```
TITULO -> FASE -> BOSS -> GAME OVER / CONTINUE -> TITULO
```

Seis cenas, todas com bundle selado e gates PASS:

| Cena | id | cpu p99 |
|---|---|---|
| TITLE | 9 | 14% |
| STAGE | 4 | 50% |
| STAGE_PLAYTEST | 5 | — (11/11 estados) |
| BOSS + arena | 6 | 78% |
| BOSS_PLAYTEST | 7 | 90% (3/3 do combate) |
| GAMEOVER / vitoria | 8 | 15% |

O titulo virou a **cena de boot**, substituindo o branding do template.
Game over expirado volta ao titulo; continue reinicia a fase.

### A tela

Gradiente noturno de 12 stops por H-int (indigo -> lavanda -> rosa), campo de
estrelas com drift lento de 1 px a cada 4 frames, silhueta de colina com arvore,
logo no terco superior e "PRESS START".

O gradiente reusa o **mesmo H-int e a mesma entrada unica de CRAM** da fase; só
a tabela muda (`RASTER_setNightSky`). Custo identico.

### Tres tentativas para uma linha de texto

"PRESS START" custou tres capturas, e as tres falhas valem registro:

1. **No plano WINDOW** — nao apareceu. O window nao tem tamanho ate
   `VDP_setWindowVPos` ser chamado.
2. **Em BG_A com `VDP_setTextPriority(TRUE)`** — saiu como bloco cinza solido
   em vez de glifos. A fonte do SGDK nao coexiste com S/H global sem tratamento.
3. **Com S/H desligado** — funcionou.

A licao generalizavel: **cena sem efeito que dependa de S/H deve rodar com S/H
desligado.** `doc/PALETTES.md` §2.2 trava S/H para cenas de GAMEPLAY por causa do
vortex de inalar; titulo e game over nao tem essa necessidade. Brigar com a fonte
custou mais que aceitar isso. Efeito colateral bem-vindo: sem S/H o gradiente
ficou visivelmente mais vivo, porque nao esta a meio brilho.

E uma quarta: o prompt piscava e duas capturas o pegaram apagado, o que e
indistinguivel de "nao renderiza". **Affordance essencial nao pisca.** Se precisa
ser provado por captura, tem de estar sempre visivel.

### A divida de audio NAO zerou, e eu nao vou fingir que zerou

A condicao de expiracao da baseline dizia: "chega a zero quando as cenas do
template forem substituidas pelo titulo proprio e `AUDIO_init`/`AUDIO_update`
sairem de `app.c`".

O titulo existe e e a cena de boot. As cenas do template (branding/menu/demo)
estao **inalcancaveis**. Mas os ARQUIVOS continuam em `src/`, e o gate faz grep
em arquivo, nao em codigo alcancavel. **As 11 violacoes seguem contadas.**

Nao deletei esses arquivos: eu nao os criei. Fica como decisao do usuario.

---

## Sessao 011 — 2026-08-06 — Copy abilities com moveset, e um bloqueio de ambiente

### O chapeu agora faz alguma coisa

Por varias sessoes o jogador engolia um inimigo e ganhava um chapeu **cosmetico**.
O loop fechava mecanicamente e nao recompensava. Agora:

| Ability | Alcance | Comportamento | Sensacao |
|---|---|---|---|
| FIRE | curto | continuo enquanto segura | pressao |
| BEAM | medio | instantaneo, sem viagem | precisao |
| CUTTER | longo | viaja e **volta** | compromisso |
| STONE | nenhum | Kirby vira pedra, cai | defesa |
| SWORD | curto | um arco forte | decisao |

Sao diferentes em **feel**, nao so em cor. O FX de 240x16 tambem as separa por
FORMA — pluma, raio irregular, crescente vazado, bloco duro, arco fino — como o
briefing R1-04 exige para um jogador daltonico.

**B faz dupla funcao, e isso e design do Kirby, nao atalho:** sem ability, B
inala; com ability, B ATACA. O jogador troca o vortex por um moveset, que e
exatamente o custo que a mecanica de copia deve ter. Os 6 inimigos concedem as 5
abilities diferentes (o ultimo nao concede nada, tambem um classico).

### Um gate novo que cobra a recompensa

`ability_moveset_fires` reprova qualquer captura que **conceda** uma ability sem
que nenhum moveset **dispare**. Esse era literalmente o estado do projeto ate
hoje. Medido: `PASS — a copy ability was granted; its moveset also fired`.

### Alavanca de degradacao gasta ANTES de quebrar

`sprites_per_scanline` mediu **19 de 20** com 6 inimigos + 8 tufos + 12 tiros nas
mesmas linhas. Um sprite do flicker. Gastei a alavanca documentada em
ARCHITECTURE.md 5 (particulas -> primeiro plano -> projeteis): camada 5 de 8 para
6 tufos. **19 -> 18.** Enemies e Kirby nao degradam, como o contrato manda.

Isso so funcionou porque a ordem de degradacao foi escrita ANTES do problema.

### O bloqueio de ambiente que custou a maior parte da sessao

Build e capturas passaram a falhar com `fallocate: Nao ha espaco disponivel`, em
0.07 s, antes de compilar. O host tinha **46 GB livres**, o que mascarou tudo.

Causa real: **`/run/user/1000` (XDG_RUNTIME_DIR, tmpfs de 1,5 GB) 100% cheio.**
O flatpak precisa de espaco la para montar o sandbox. Os 1,5 GB inteiros eram
`codex-desktop/tmp/pytest-of-misael` — tres `Metroid.state` de 512 MB, de testes
de OUTRO aplicativo. **Nao deletei: nao sao meus.** Foram removidos por fora e o
build voltou.

Isso provavelmente tambem explica os `window_timeout` intermitentes do BlastEm,
que eu havia atribuido a processos orfaos. **Aquele diagnostico estava incompleto**
e a correcao esta registrada.

### Quarta ocorrencia do mesmo erro meu

`str.replace` que nao casa por espacamento e falha em SILENCIO. Quarta vez nesta
sessao. Passei a usar a ferramenta de edicao que falha alto, e a conferir por
`grep` antes de buildar.

### Gates

```
sprites/frame 25/80 | sprites/scanline 18/20 | cpu p99 60/100
playtest 11/11 locomocao | ability_moveset_fires PASS | 0 frames acima do budget
```

---

## Sessao 012 — 2026-08-06 — R3 + R4: a agua

### Os dois efeitos existem em ROM, provados por dado e nao por screenshot

**R4 (troca de paleta submersa)** verificado no dump de CRAM, nao no olho:

```
lake_w4   PAL1[1..5] =  72,180,72 | 36,144,36 | 36,108,36 | 144,108,72 | 108,72,36
lake_fix  PAL1[1..5] =   0,108,180 | 0,144,216 | 36,144,216 | 36,180,252 | 108,72,36
                        ^-------- 4 words trocados --------^   ^-- intacto
```

Exatamente os 4 words configurados. A rampa submersa vem da regra que o estudo
de arte r1-06 propos, materializada como **tabela** e nao como aritmetica cega —
aritmetica cega achata materiais diferentes na mesma cor, que era o alerta do
proprio estudo.

**R3 (distorcao senoidal por linha)** visivel na captura, e custa quase nada:
sao entradas da tabela de HScroll que ja sao reconstruidas.

### A tensao do meu proprio contrato, resolvida medindo

`doc/PALETTES.md` §6.1 limitava o H-int a **1 word de CRAM por faixa**, com o teto
real marcado `[NAO MEDIDO]`; a §6.3 descrevia uma troca de **16 words**. As duas
coisas nao podiam ser verdade.

Em vez de escolher uma, tornei a contagem **configuravel** (`RASTER_setWaterCramWords`)
para que uma captura possa subir o numero ate aparecer lixo. Com **4 words**
nao ha corrupcao. O teto real segue `[NAO MEDIDO]`, mas agora existe o
instrumento para medi-lo, e 4 esta provado.

### Dois bugs meus, ambos com a mesma raiz: pressuposto nao verificado

1. **A otimizacao da arena do boss quebrou o R3.** "Pular o rebuild quando a
   camera nao move" tambem pula quando a distorcao e ANIMADA. Camera parada nao
   significa tabela estatica. Toda otimizacao de cache precisa listar o que a
   invalida.
2. **O R4 nunca disparava.** Eu derivava a scanline de `stop * 12`, mas `stop`
   SATURA em 12, entao a linha travava em 144 e a linha d'agua estava em 150.
   Nao se reutiliza um contador que satura como se fosse relogio.

### Um defeito que fica aberto, de proposito

Depois dessas mudancas a primeira parada do gradiente de ceu passa a durar mais
scanlines, em ambas as cenas. **Nao determinei a causa.** O H-int esta correto na
leitura, o reset acontece em `RASTER_frameStart`, e todos os gates passam
(parallax exato, cpu p99 59%, 0 frames acima do budget).

**Nao vou consertar por comparacao de screenshot** — foi exatamente o erro que
custou uma sessao inteira na medicao de parallax. A correcao certa e exportar
`s_skyStop` e `s_hintLine` no bloco KRB1 e LER os valores. Registrado como
defeito aberto dentro do proprio `raster.c`, para quem mexer nele depois.

### Correcao: o efeito estava bonito e nao cabia no frame

Depois de ver a captura do lago funcionando eu ia declarar R3/R4 prontos. Rodei
os gates e eles diziam outra coisa:

| | antes | depois |
|---|---|---|
| cpu p99 | **111%** | **71%** |
| frames acima do budget | **306** | **0** |
| `parallax_layer_speeds` | FAIL | PASS (4/4 exato) |

Duas causas, ambas minhas:

1. **`F16_sin()` uma vez por linha por frame**, ~74 linhas. Substituido por uma
   tabela de 64 entradas: mesma imagem, 40 pontos de CPU a menos. Trigonometria
   por frame no Mega Drive e quase sempre tabela, nao funcao.
2. **O gate de parallax lia duas coisas na mesma amostra.** A telemetria
   publicava `s_hscrollA[200]`, que agora soma parallax + ondulacao. Passei a
   publicar `-cameraX`, que e a grandeza que o gate realmente mede.

A licao registrada: **screenshot nao mede tempo.** Um efeito pode estar
visualmente perfeito e nao caber no orcamento.

---

## Sessao 013 — 2026-08-06 — R5: o holofote, e duas licoes caras sobre otimizacao

### O contrato de Shadow/Highlight finalmente foi exercitado

R5 e o unico efeito que usa os **operadores** que eu reservei em `PAL3[14]` e
`PAL3[15]` la na FASE 0. Um sprite com esses indices nao desenha cor: ele
CLAREIA ou ESCURECE o que esta embaixo. E a unica pseudo-transparencia real do
Mega Drive.

Escolhi **clarear** em vez de escurecer o resto de proposito: escurecer o
entorno exigiria tiles de fundo em prioridade 0, que o gate P5 proibe — e proibe
com razao, porque um tile em prioridade 0 nao intencional e indistinguivel
disso. `tile_priority_under_sh` segue **0 de 13 amostrados**.

E o efeito tem regra de gameplay, como a FILOSOFIA MAXIMALISTA exige:
**Whispy so toma dano enquanto esta iluminado.** O contra-ataque tem de ser
cronometrado com a varredura, nao repetido.

### Duas licoes que custaram quatro capturas

**1. Tabela nao e automaticamente mais rapida que funcao.**

Troquei `F16_cos/F16_sin` da cadeia do boss por uma tabela de 64 entradas,
esperando o mesmo ganho de 40 pontos que a tabela deu na agua. Deu o contrario:

| | cpu p99 | frames estourados |
|---|---|---|
| com `F16_sin` | 92% | 3 |
| com "tabela" | **107%** | **225** |

Meu indexador fazia `deg % 360` e `deg * 64 / 360` — **duas divisoes de 32 bits
por segmento**, e o 68000 nao tem divisao rapida. A tabela ganhou em `raster.c`
porque o indice era uma MASCARA (`& 63`); perdeu aqui porque exigiu divisao.
**O que importa e o custo do indice, nao a existencia da tabela.** Revertido.

**2. Gastei degradacao antes de procurar desperdicio.**

Quando a arena foi a 106% eu peguei direto a alavanca 2 do §5.1 (7 -> 5
segmentos do galho), violando a licao que eu mesmo tinha registrado na sessao
da arena. Ela funcionou (106% -> 92%), o que mascarou o erro de ordem.

E quando a degradacao for mesmo necessaria, **deve pagar quem causou o custo**:
o holofote e a feature nova, entao ele foi de 5 para 3 sprites e resolveu os 3
frames restantes — em vez de cortar mais o boss.

```
r5_light   106%  289 frames   (5 luzes, 7 segmentos)
r5_lever2   92%    3 frames   (5 luzes, 5 segmentos)
r5_final    82%    0 frames   (3 luzes, 5 segmentos)
```

### Os cinco efeitos raster do contrato existem

R1 gradiente de ceu, R2 bandas de parallax, R3 distorcao da agua, R4 paleta
submersa, **R5 holofote**. Todos em ROM, todos com gate passando.

---

## Sessao 014 — 2026-08-06 — Pacote de assets de producao (P1)

### A inversao de uma proibicao, com justificativa medida

O pacote R1 **proibia** os papeis `animated_sprite_final` e `res_direct` — a
regra do workspace parte de que IA nao acerta grade de 8 px, paleta indexada e
deduplicacao de tile. O P1 pede exatamente isso.

A inversao nao e por conveniencia. E porque o loop R1→R2→R3 mediu o contrario:
**11 entregas com 0.00% de pixels ilegais em RGB333**, e o R3 fechou reduzindo
paleta sem introduzir uma cor nova. O executor provou a capacidade especifica
que a proibicao protegia.

### 16 assets, todos de uma vez

`doc/art/PRODUCTION_ASSET_PACK.md` + `doc/art/production_asset_manifest.json`.

O ponto que mais importa e que **as dimensoes nao sao negociaveis**:
`res/resources.res` declara o tamanho do sprite em tiles e o codigo indexa frames
por posicao. Um pixel a mais quebra o build ou desalinha a animacao inteira. Por
isso cada asset vem com largura, altura, contagem de frames, ordem dos frames e
paleta travada.

Tres restricoes carregam licoes anteriores:

1. **A chave `255,0,255` e cor RESERVADA**, excluida da quantizacao. No R1-03 o
   quantizador a moveu para `(255,0,219)` em 56% dos pixels.
2. **PAL3[14] e PAL3[15] sao proibidos como cor** — sao os operadores de
   Shadow/Highlight, e o holofote do boss depende deles.
3. **A escada de valor das 5 camadas e normativa**, com a formula de luminancia
   escrita junto (diretor e executor ja mediram a mesma imagem com formulas
   diferentes uma vez).

E um asset esta marcado **NAO DESENHE**: `ph_light.png` nao e arte, e uma
mascara de operador onde todo pixel opaco e o indice 14.

### O validador, e o autoteste que o justifica

`tools/harness/validate_assets.py` julga o que script PODE julgar: dimensao
exata, legalidade RGB333, chave de transparencia, teto de cores, escada de valor,
ladrilhamento horizontal e os vaos obrigatorios do terreno.

Duas coisas que fiz de proposito:

- **Zero entregas NAO e `pass`.** A primeira versao reportava
  `delivered 0/16, failed 0 -> pass`, que e o passe vacuoso contra o qual lutei o
  projeto inteiro. Agora reporta `status=empty` e sai com codigo != 0.
- **`--self-test`** roda os mesmos checks contra os placeholders atuais, para
  provar que eles disparam. Achou **costura de ladrilhamento em 3 assets** que eu
  nao sabia que existia, e mostrou a escada de valor com numeros reais:
  `B2 0.511 · B3 0.419 · B4 0.361 · B5 0.308`, monotonica.

O validador diz explicitamente, no proprio output, que julga **conformidade e
nunca qualidade** — se a arte e boa continua sendo decisao humana.
