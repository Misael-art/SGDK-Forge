# ARCHITECTURE.md — Contrato Tecnico Mestre

> **Projeto:** KIRBY_FAN GAME GROK BUILD [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]
> **Status deste documento:** `documentado` — nenhuma linha abaixo esta `testado_em_emulador`
> ate existir bundle BlastEm selado que a comprove.
> **Fase:** FASE 0 (contrato). Nenhum codigo de jogo pode ser escrito contra uma
> afirmacao deste documento que ainda esteja marcada `[NAO MEDIDO]`.


## 0.1 Lineage Grok Build (2026-08-08)

Este documento e a autoridade tecnica do **GROK BUILD**. Herda medicoes e
decisoes validadas no prior art CLOUDE (mesmo host, mesma stack SGDK 2.11),
mas a evidencia de ROM, arte e scores de critico desta arvore comecam do zero.

Objetivo de qualidade visual/sonora: teto Alien Soldier / Gunstar Heroes /
Dynamite Headdy / Streets of Rage 2 / Demons of Asteborg / ZPF / Xeno Crisis.

Documentos irmaos, todos normativos: [VRAMMAP.md](VRAMMAP.md),
[PALETTES.md](PALETTES.md), [SOUNDMAP.md](SOUNDMAP.md).

---

## 0. Regra de leitura

Este documento distingue tres tipos de afirmacao. A distincao e obrigatoria e
qualquer revisor deve rejeitar texto que a viole:

| Marca | Significado |
|---|---|
| `[VERIFICADO]` | Extraido de header/fonte do SGDK 2.11 ou medido em runtime. Tem citacao. |
| `[DECIDIDO]` | Escolha de projeto. Nao e fato de hardware. Pode mudar com registro no changelog. |
| `[NAO MEDIDO]` | Estimativa/orcamento alvo. **Bloqueia claim de pronto.** So vira numero real via harness. |

---

## 1. O que este jogo e

Reimaginacao para Mega Drive de **Kirby's Adventure (NES, 1993)**.

Nao e um port 1:1 de dados. E uma releitura: mesma fantasia (inalar, copiar
poder, flutuar), mesma paleta emocional (ceu pastel, terreno de doce, motivo de
estrela), mas resolvida com o vocabulario visual do Mega Drive — raster, scroll
por linha, Shadow/Highlight, FM — em vez do vocabulario do NES (bankswitch de
CHR, atributo 16x16, flicker).

### 1.1 Tese de design

O Kirby's Adventure do NES e famoso por *tentar* coisas que o NES nao suportava:
gradientes de ceu, camadas de profundidade, cores por regiao. O trabalho deste
projeto e **entregar aquilo que o jogo original estava alcancando**, nao apenas
redesenhar o que ele conseguiu.

Consequencia pratica, e este e o criterio criativo dominante do projeto:

> Todo cenario precisa responder a pergunta "o que o NES nao conseguiu fazer aqui?"
> com uma tecnica de MD nomeada, com owner e budget. Cenario que nao responde
> essa pergunta e cenario reprovado, mesmo que bonito.

### 1.2 Escopo VER.001 (o que realmente entregamos)

`[DECIDIDO]` Fatia vertical em qualidade final, nao jogo inteiro em qualidade media.

```
TITULO  ->  VEGETABLE VALLEY 1  ->  2  ->  3  ->  BOSS (Whispy Woods)  ->  GAME OVER / CONTINUE
```

- 3 fases jogaveis + 1 arena de boss
- 5 copy abilities: FIRE, BEAM, CUTTER, STONE, SWORD
- ~12 tipos de inimigo, dos quais 5 dao copy
- 1 boss multi-articulado

**Fora de escopo VER.001, declarado agora para impedir feature creep:**
mundos 2-7, mini-games, museu de habilidades, save/password, modo 2P,
Meta Knight, Nightmare. Ver [19-roadmap-risk-register.md](19-roadmap-risk-register.md).

### 1.3 Nota legal, declarada de uma vez

Kirby e propriedade da Nintendo/HAL Laboratory. Este e um **fan game nao
comercial**. Consequencias que sao regra de engenharia, nao so juridica:

- Nenhum asset extraido da ROM do NES entra neste repositorio. Toda arte e
  original, autoral, feita para este projeto.
- Nenhuma trilha e rip. Toda musica e composicao original no espirito do jogo.
- A ROM final nao pode ser vendida nem distribuida como produto.

Detalhes em [20-release-marketing-legal.md](20-release-marketing-legal.md).

---

## 2. Alvo de hardware

| Parametro | Valor | Fonte |
|---|---|---|
| Video | 320x224, H40, NTSC 60 Hz | `[DECIDIDO]` alvo primario |
| PAL | 320x240 @ 50 Hz, timing derivado | `[DECIDIDO]` secundario, gate separado |
| ROM | <= 4 MB, sem mapper | `[DECIDIDO]` restricao do brief |
| Work RAM | 64 KB, pools estaticos, zero `malloc` | AGENTS.md — restricao nao negociavel |
| VRAM | 64 KB | fixo do VDP |
| CRAM | 4 paletas x 16 = 64 entradas | fixo do VDP |
| Audio | YM2612 6 FM (ch6 = DAC) + PSG 3+1, driver XGM | `[DECIDIDO]` |

### 2.1 Enderecos default do VDP no SGDK 2.11 `[VERIFICADO]`

Extraidos de `sdk/sgdk-2.11/src/vdp.c:23-27`:

```
WINDOW_DEFAULT   0xD000
BPLAN_DEFAULT    0xC000   (BG_B)
APLAN_DEFAULT    0xE000   (BG_A)
HSCRL_DEFAULT    0xF000
SLIST_DEFAULT    0xF400
```

`VDP_MAPS_START` = menor desses = `0xC000`, logo `TILE_SPACE` = 48 KB e
`TILE_MAX_NUM` = 48128/32 = **1536 tiles** (`inc/vdp.h:224-230`).

Reservas do SGDK `[VERIFICADO]` (`inc/vdp.h:240-260`, `src/sprite_eng.c:157`):

```
TILE_SYSTEM_INDEX  0      TILE_SYSTEM_LENGTH  16     -> tiles 0..15
TILE_USER_INDEX    16
FONT_LEN           96     TILE_FONT_INDEX     1440   -> tiles 1440..1535
SPR_init() default spriteVramSize = 420             -> tiles 1020..1439
```

Sobra para tiles de fundo no default: **1004 tiles**. Esse numero e o orcamento
real e esta detalhado em [VRAMMAP.md](VRAMMAP.md), que e a autoridade sobre VRAM.

---

## 3. A decisao arquitetural central: como fazer 4+ camadas com 2 planos

O brief exige "minimo 4 camadas com velocidades independentes". O Mega Drive tem
**dois planos de scroll e uma window**, e a window nao rola. AGENTS.md lista
"Terceiro plano BG" explicitamente como alucinacao.

`[DECIDIDO]` Resolvemos assim, e esta e a espinha visual do projeto inteiro:

```
                            fonte              velocidade         custo
CAMADA 1  ceu / gradiente   BG_B, banda 0      0 (estatico)       H-int, ~0 tiles
CAMADA 2  montanhas longe   BG_B, banda 1      1/8 do jogador     line-scroll
CAMADA 3  colinas perto     BG_B, banda 2      1/3 do jogador     line-scroll
CAMADA 4  terreno jogavel   BG_A               1/1                scroll normal
CAMADA 5  primeiro plano    sprites            5/4 (parallax neg) orcamento de sprite
```

**Camadas 1-3 sao o MESMO plano BG_B**, separadas por bandas de scanline com
valores diferentes na tabela de HScroll. Isso e a tecnica de line-scroll da
escola Ranger X / Sonic, nao um terceiro plano. O custo real e:

- tabela de HScroll de 224 linhas x 4 bytes = 896 bytes, escrita por DMA em VBlank
- CPU para preencher a tabela: `[NAO MEDIDO]` — orcamento alvo <= 8 scanlines/frame

**Camada 5 come orcamento de sprite**, entao ela e um recurso caro e sazonal: so
existe em trechos onde a contagem de inimigos e baixa. Isso e uma regra de level
design, nao um detalhe tecnico, e esta em [16-ldd.md](16-ldd.md).

### 3.1 Por que isso importa para o critico

Quando o critico da FASE 2 comparar nossa captura com Ranger X ou Demons of
Asteborg e disser "o fundo deles tem mais profundidade", a resposta acionavel
nao e "adicionar um plano" — e uma destas, em ordem de custo:

1. aumentar o numero de bandas de line-scroll em BG_B (barato, CPU)
2. variar a velocidade *dentro* de uma banda (parallax continuo por linha)
3. adicionar column-scroll em BG_A para profundidade vertical
4. gastar sprites em camada 5
5. trocar paleta por banda via H-int, para separar as camadas por cor alem de velocidade

Item 5 e o mais subestimado e e onde o Mega Drive ganha do NES de forma mais
visivel. Ver [PALETTES.md](PALETTES.md).

---

## 4. Efeitos raster — o orcamento de H-interrupt

`[VERIFICADO]` SGDK expoe `SYS_setHIntCallback()` (`inc/sys.h:387`), callback
prefixado com `HINTERRUPT_CALLBACK` (`inc/sys.h:52`), e `VDP_setHIntCounter()`
(`inc/vdp.h:846`).

O H-int e o recurso mais escasso e mais mal usado do MD. Regra do projeto:

> **Um unico H-int callback no jogo inteiro.** Ele e uma maquina de estados
> dirigida por uma tabela de faixas compilada por cena, nao um lugar onde cada
> sistema pendura seu efeito.

`[DECIDIDO]` Estrutura da tabela de faixas (por cena, gerada em VBlank, consumida
em H-int):

```c
typedef struct {
    u8  line;        // scanline em que a faixa comeca
    u8  action;      // RASTER_PAL_SWAP | RASTER_HSCROLL_BAND | RASTER_BGCOL | ...
    u16 arg0;        // significado depende de action
    u16 arg1;
} RasterBand;
```

Restricoes duras do H-int, todas nao negociaveis:

- o callback nao aloca, nao chama funcao de biblioteca, nao toca no XGM
- escreve **no maximo** o que cabe no blanking horizontal; escrita de paleta
  no meio da linha visivel gera lixo em hardware real — por isso troca de
  paleta so em faixas cujo limite foi validado em BlastEm **e** anotado
- orcamento alvo: `[NAO MEDIDO]`, teto <= 16 faixas ativas por cena

### 4.1 Catalogo de efeitos raster do VER.001

| # | Efeito | Onde | Mecanismo | Gate |
|---|---|---|---|---|
| R1 | Gradiente de ceu | todas as fases externas | troca de cor de fundo por faixa | cor legal RGB333 |
| R2 | Bandas de parallax | todas | HScroll por linha | 4 camadas visiveis |
| R3 | Distorcao de agua | fase 2, abaixo da linha d'agua | HScroll senoidal por linha | sem tearing |
| R4 | Faixa de paleta submersa | fase 2 | troca de PAL1 na linha d'agua | 1 troca, nao 224 |
| R5 | Holofote | arena do boss | Shadow/Highlight + faixa | ver PALETTES.md |

Cada um desses **precisa** de efeito colateral de gameplay (FILOSOFIA
MAXIMALISTA, AGENTS.md). R3 nao e enfeite: abaixo da linha d'agua a fisica do
Kirby muda. R5 nao e enfeite: fora do holofote o boss nao pode ser atingido.

---

## 5. Sprites, e o problema real do Mega Drive

`[VERIFICADO]` Limites do VDP em H40: 80 sprites/frame, 20 sprites/scanline,
320 pixels de sprite por scanline. Ultrapassar corta sprites — nao e "lentidao",
e desaparecimento.

`[DECIDIDO]` Orcamento por cena, alocado como cotas fixas para que nenhum
sistema possa canibalizar outro:

| Consumidor | Cota sprites/frame | Nota |
|---|---|---|
| Kirby + chapeu de habilidade | 8 | chapeu e sprite separado, troca sem redesenhar Kirby |
| Inimigos | 32 | pool fixo de 12 entidades |
| Projeteis | 12 | pool fixo |
| Particulas | 16 | pool fixo, degrada primeiro sob pressao |
| Camada 5 (primeiro plano) | 8 | sazonal, ver 3.0 |
| HUD (fora da window) | 4 | |
| **Total** | **80** | teto duro |

Regra de degradacao sob pressao, em ordem: particulas -> camada 5 -> projeteis.
**Inimigos e Kirby nunca degradam.** Flicker so e aceito se for essa politica
declarada; flicker acidental e bug, nao estilo.

### 5.1 Boss multi-articulado — Whispy Woods

`[DECIDIDO]` O boss e o teste de estresse do projeto e por isso e o primeiro
sistema pesado a ser construido, nao o ultimo.

```
tronco          BG_A (tiles, nao sprite)      0 sprites
rosto           sprite composto               6 sprites
galho x4        cadeia de 7 segmentos         28 sprites
maca/projetil   pool                          8 sprites
particula       folhas, rajada de ar          16 sprites
                                              --------
                                              58 sprites  <= 80  OK
```

Angulacao dos galhos: cinematica direta com tabela de seno em `fix16`. **Zero
float** (AGENTS.md). O segmento *n* herda o angulo acumulado do segmento *n-1*;
a suavidade vem de interpolar o angulo alvo, nao de aumentar a contagem de
segmentos.

`[NAO MEDIDO]` Custo de CPU da cadeia de 28 segmentos por frame. Se estourar,
a ordem de corte e: interpolar a cada 2 frames -> 5 segmentos por galho ->
3 galhos. Nunca cortar frames de animacao do rosto.

---

## 6. Estrutura de codigo

```
src/
  core/         app.c, loop principal, maquina de cenas
  scenes/       scene_title, scene_stage, scene_boss, scene_gameover
  entities/     kirby.c, enemy.c, projectile.c, particle.c   (pools estaticos)
  systems/      raster.c, parallax.c, camera.c, collision.c, feel.c
  audio/        xgm_router.c   (dono unico dos canais, ver SOUNDMAP.md)
  system/       runtime_probe.c  (telemetria VLAB — nao e codigo de jogo)
inc/            espelha src/
res/            resources.res + assets convertidos
data/source_art/  fontes de arte (PNG grandes), nunca entram na ROM
tools/harness/  build_and_capture.sh, gates.py, imagediff.py, frametime.py
doc/            este contrato + GDD/TDD/LDD + licoes
```

### 6.1 Regra de dono unico para sistemas acoplados

Do brief, regra dura 2. Aplicada aqui de forma nominal:

| Sistema acoplado | Dono unico | Ninguem mais escreve |
|---|---|---|
| scroll + paleta + raster | `systems/raster.c` | tabela de HScroll, CRAM em H-int, cor de fundo |
| audio + timing de DMA | `audio/xgm_router.c` | canais FM/PSG, janela de DMA de audio |
| alocacao de VRAM | `systems/vram_budget.c` | indices de tile, regiao de sprite |

Se dois sistemas precisam do mesmo recurso, eles **pedem ao dono**, em ordem
sequencial dentro do frame. Nao existe escrita concorrente.

### 6.2 Ordem do frame `[DECIDIDO]`

```
VBlank IN
  1. DMA fila do frame anterior         (tiles animados, paleta, HScroll)
  2. SPR_update()
  3. XGM tick
VBlank OUT
  4. input
  5. entidades (kirby -> inimigos -> projeteis -> particulas)
  6. colisao
  7. camera
  8. game feel (hit-stop pode abortar 5-7 no proximo frame)
  9. montar tabela de HScroll do proximo frame
 10. enfileirar DMA
 11. probe tick
```

DMA **so** no passo 1. AGENTS.md: "DMA fora do VBlank — apenas seguro no VBlank
callback". Nao existe excecao neste projeto.

---

## 7. Game feel — os numeros

Adjetivo vira medicao (regra dura 3 do brief). "Impacto satisfatorio" nao e
especificacao; isto e:

| Efeito | Parametro | Valor `[DECIDIDO]` |
|---|---|---|
| Hit-stop | frames congelados no acerto | 4 (normal), 8 (finalizacao) |
| Screen shake | amplitude / decaimento | 3 px / -1 px por 2 frames |
| Flash de impacto | mecanismo | troca de PAL por 2 frames, **nao** sprite branco |
| Knockback | arco | vy inicial -2.5 px/f, gravidade 0.25 px/f2, em `fix16` |
| Smear frame | duracao | exatamente 1 frame, so em dash e ataque de espada |
| Coyote time | frames apos sair da borda | 4 |
| Buffer de pulo | frames antes de tocar o chao | 5 |

Todos esses valores sao `[DECIDIDO]` e **serao contestados pelo critico da
FASE 2**. Eles existem para poder ser medidos e mudados, nao porque estao certos.

---

## 8. Criterios mensuraveis de "pronto" por subsistema

Nenhum subsistema pode ser declarado pronto sem que **todas** as linhas da sua
coluna passem no harness. Isto e o contrato que a FASE 2 cobra.

| Subsistema | Pronto quando |
|---|---|
| **Parallax** | 4 camadas distinguiveis em captura; velocidades medidas e distintas; 0 tearing em 600 frames; custo <= 8 scanlines/frame |
| **Raster** | os 5 efeitos R1-R5 ativos; toda cor CRAM legal em RGB333; 0 lixo em faixa de troca; H-int <= 16 faixas |
| **Sprites** | pico medido <= 80/frame e <= 20/scanline em todas as cenas; 0 flicker nao declarado |
| **VRAM** | uso total medido <= mapa de VRAMMAP.md; 0 estouro em 600 frames; planos sem sobreposicao com area de tile |
| **Paletas** | <= 61 cores simultaneas; politica de Shadow/Highlight documentada e observada |
| **Performance** | p99 de CPU load dentro do orcamento; 0 frames acima do budget na cena mais pesada |
| **Audio** | 0 roubo de canal fora de regra do SOUNDMAP; DAC sem clip; musica nao engasga em DMA pesado |
| **Kirby (controle)** | 100% dos estados do jogador cobertos por playtest scriptado |
| **Boss** | 58 sprites medidos; ciclo completo sem estouro; derrota e vitoria alcancaveis por input scriptado |
| **Game feel** | valores da secao 7 verificados frame a frame em captura |

---

## 9. Estado do harness e do host

`[VERIFICADO]` em 2026-07-29, neste host Linux:

- **Build:** unica rota funcional e
  `tools/sgdk_wrapper/build_sgdk_wine_bridge.sh --project-root <proj>`
  (flatpak Wine). Retorna `wine_bridge_status=buildado`. Produziu
  `out/rom.bin` (131072 B no template puro, 262144 B apos o probe).
- **`tools/sgdk_wrapper/build.sh` esta quebrado em Linux.** Causa: `env.sh`
  prepende `$GDK/bin` no PATH, e esse diretorio tem symlinks `cp -> cp.exe`,
  `mkdir -> mkdir.exe`, `rm -> rm.exe`; coreutils sao sombreados por binarios
  Windows que nao entendem caminho POSIX. Mesmo defeito derruba
  `new_project.sh`. Registrado em [licoes](agent_learning/), nao corrigido —
  `tools/sgdk_wrapper/` e canonico e exige aprovacao humana.
- **Captura:** `capture_blastem_evidence_linux.sh` roda BlastEm via flatpak em
  X11, tira screenshot, salva SRAM e sela bundle. Rodou; janela reportou
  `60.3 fps`; gate semantico de screenshot passou.
- **Graphify** nao fica `fresh` neste host (mesma classe de bug de caminho em
  `graphify_forge.ps1:53`). Graphify e indice consultivo, nunca fonte de
  verdade (AGENTS.md), entao isso nao bloqueia producao — mas bloqueia o guard
  `assert_agent_environment.ps1`, que retorna `blocked reason=prepare_failed`.

### 9.1 Telemetria VLAB — como qualquer numero deste documento vira medicao

O selador `tools/sgdk_wrapper/seal_fresh_evidence_bundle.py` procura o ASCII
`VLAB` na SRAM, le `>HH` (schema, total_bytes) em +4 e `(total_bytes-8)/2`
words big-endian em +8. Words 0..23 = metricas, 24.. = as 64 entradas de CRAM.

A ROM **precisa** emitir esse bloco ou nenhuma evidencia e aceita. A implementacao
de referencia esta em `SGDK_projects/Celestial Chase Revive .../src/system/runtime_probe.c`
e ja mede: CPU load, frames acima do budget, jitter, pico de sprites por
scanline, `SPR_getUsedVDPSprite`, `SPR_getNumActiveSprite`, enderecos de plano,
modos de scroll e as 64 cores de CRAM.

**Esse bloco e o que transforma este contrato em algo cobravel.** Sem ele,
todo numero aqui e opiniao.

### 9.2 Primeira medicao real `[VERIFICADO]` 2026-07-29

O probe VLAB foi portado para este projeto e a ROM **do template** (sem nada de
Kirby ainda) produziu dois bundles com `status: sealed`, `blockers: []`, contendo
`rom`, `screenshot`, `sram`, `vdp_dump` e `runtime_metrics`:

```
out/evidence/probe_vlab_smoke/blastem-linux-20260729T150455Z-212306/
out/evidence/probe_scene_demo/blastem-linux-20260729T150654Z-218744/
```

Numeros medidos na cena `scene_demo` (cena vazia, so texto):

| Metrica | Medido | Teto | Veredito |
|---|---|---|---|
| Cores simultaneas nao transparentes | 21 | 61 | pass |
| Entradas de CRAM ilegais em RGB333 | 0 | 0 | pass |
| Sprites/frame | 0 | 80 | pass (nao ha sprite ainda) |
| Sprites/scanline | 0 | 20 | pass (amostrado, nao exaustivo) |
| Frames acima do budget | 0 | 0 | pass |
| CPU load p50 / p95 / p99 / pior | 36 / 36 / 42 / 42 | 100 | pass |
| Planos sobrepostos com area de tile | 0 | 0 | pass |

Enderecos de plano lidos em runtime confirmam os defaults da secao 2.1:
`bg_a = 0xE000`, e todas as tabelas disjuntas.

**Atribuicao por secao, em scanlines/frame** — este e o numero mais importante
que temos hoje, porque e o orcamento real de onde tudo vai sair:

```
input          2
scene         90
audio          1
sprite         4
vblank_idle  171     <- folga disponivel
```

Leitura honesta disso: a `scene_demo` gasta 90 scanlines desenhando **texto**,
o que e caro e vai embora. As 171 scanlines de `vblank_idle` sao a folga bruta
para parallax + raster + entidades + boss. Isso **nao** prova que o jogo cabe;
prova que existe folga mensuravel e que o instrumento para cobrar funciona.

Dois gates retornaram `warn`, ambos corretamente:
- `sprites_observed` — nao existe sprite no projeto ainda
- `vram_tile_budget` — `doc/VRAMMAP.md` ainda nao existe, entao o gate avisa
  em vez de reprovar, conforme contratado

Consequencia para a secao 4: o orcamento alvo de "<= 8 scanlines/frame" para a
tabela de HScroll continua `[NAO MEDIDO]` — ainda nao existe line-scroll no
codigo. Mas agora existe o instrumento que vai medi-lo.

---

## 10. Riscos arquiteturais conhecidos

| # | Risco | Probabilidade | Mitigacao |
|---|---|---|---|
| A1 | 1004 tiles de fundo nao bastam para 4 camadas ricas | **alta** | streaming de tile por sala; reciclar font (+96); reduzir sprite VRAM |
| A2 | H-int + line-scroll + DMA de tile animado competem pelo mesmo VBlank | alta | dono unico (`raster.c`); orcamento de DMA por frame em VRAMMAP.md |
| A3 | Cadeia de 28 segmentos do boss estoura CPU | media | degradacao declarada na secao 5.1 |
| A4 | XGM + DMA pesado -> engasgo de musica | media | janela de DMA reservada, ver SOUNDMAP.md |
| A5 | Arte original em volume AAA e o gargalo real, nao o codigo | **alta** | pipeline de imagegen com prompts versionados; ver `doc/art/` |
| A6 | Shadow/Highlight muda o significado de todas as paletas | media | decidido e travado em PALETTES.md antes de qualquer arte final |

`A5 e o risco dominante do projeto.` Codigo de Mega Drive e um problema
conhecido; produzir centenas de tiles e frames de animacao originais em
qualidade Gunstar Heroes nao e. O plano de arte precisa comecar em paralelo
com a FASE 1, nao depois.

---

## 11. Changelog deste contrato

| Data | Mudanca |
|---|---|
| 2026-07-29 | v1 inicial. FASE 0. Rota de build e captura verificadas no host. Decisao de 5 camadas via line-scroll travada. Nenhum numero de performance medido ainda. |
