# SOUNDMAP.md — Contrato de Audio

> **Dono unico:** `audio/xgm_router.c`. Nenhum outro sistema toca canal de FM,
> PSG ou PCM, nem a janela de DMA de audio. Ver [ARCHITECTURE.md](ARCHITECTURE.md) §6.1.
> **Status:** `documentado`. Nada aqui foi ouvido rodando.
> Marcas: `[VERIFICADO]` tem citacao. `[DECIDIDO]` e escolha. `[NAO MEDIDO]` bloqueia pronto.

---

## 1. XGM ou XGM2 — a decisao, e ela nao era obvia

`[VERIFICADO]` Comparacao real, dos headers do SGDK 2.11:

| | XGM v1 (`inc/snd/xgm.h:9`) | XGM2 (`inc/snd/xgm2.h:9-10`) |
|---|---|---|
| Canais PCM | **4** | **3** |
| Taxa | **14 kHz** fixa | 13.3 kHz ou 6.65 kHz, **por canal** |
| Prioridade de SFX | 16 niveis | 16 niveis |
| Controle de volume/envelope FM e PSG | **nao** | **sim** |
| Multi-track com PCM compartilhado | nao | sim (`bin/rescomp.txt`) |

**O XGM v1 ganha em canais e em taxa.** 4 canais a 14 kHz e melhor que 3 a
13.3 kHz, e 14 kHz esta dentro da faixa que o brief pediu ("~14-22 kHz").

### 1.1 A decisao `[DECIDIDO]`

> **XGM2.**

**O fator decisivo e ducking.** O brief exige que o PCM de voz/impacto "nao
asfixie a musica" — isso e ducking, e ducking exige abaixar o volume da musica
enquanto o sample toca. Apenas o XGM2 tem "adjustable volume (FM and PSG only)"
(`bin/rescomp.txt`). Com XGM v1 **nao existe ducking**: ou o sample estoura por
cima da musica, ou se abaixa o sample e ele perde impacto. Nao ha terceira opcao.

Fatores secundarios, ambos reais:

1. **Prior art medido nesta mesma stack.** O projeto
   `Celestial Chase visual benchmark` rodou XGM2 e mediu:
   `max_xgm2_cpu_load = 92`, `max_dma_wait = 0`, `missed_frames = 1` em
   `driver_frames = 1363`. Reaproveitar caminho validado custa menos que
   revalidar outro.
2. **6.65 kHz por canal corta o custo de ROM pela metade** em samples longos onde
   a banda alta nao importa (rumor, vento, passo).

### 1.2 O que a decisao custa, declarado

`[VERIFICADO]` `xgm2.h:185`: "music may use the first PCM channel so it's better
to use channel 2 to 4 for SFX". (O header diz "2 to 4" mas so existem 3 canais —
erratum da doc do SGDK; o correto e 2 e 3.)

Consequencia dura: **sobram 2 canais de PCM para SFX**, nao 3.

Cenario do brief — "Kirby inalando enquanto 3 inimigos morrem" = 4 SFX no mesmo
frame, com 2 canais. **Dois vao ser descartados.** Isso nao e bug, e a politica de
§3, e ela precisa ser boa o suficiente para que o jogador nunca perca o som que
importa.

### 1.3 Correcao ao brief: 13.3 kHz, nao 14-22 kHz

O brief pediu PCM "~14-22 kHz 8-bit". `[VERIFICADO]` `bin/xgm2.txt`:

> "PCM playback rate is fixed to ~13.3 Khz (full speed) or ~6.65Khz (half speed)
> and can be selected on a channel basis."

**A taxa nao e escolha nossa. E 13.3 kHz ou 6.65 kHz.** Regra dura 4: medicao
contradiz o brief, segue a medicao e documenta. Nao existe 22 kHz no XGM2.

---

## 2. Propriedade de canal

`[DECIDIDO]` Tabela normativa. `xgm_router.c` e o unico escritor.

| Canal | Papel | Dono | SFX pode roubar? |
|---|---|---|---|
| FM 1 | baixo FM | musica (XGM2) | **NAO** |
| FM 2 | acompanhamento / pad | musica (XGM2) | **NAO** |
| FM 3 | lead melodico | musica (XGM2) | **NAO** |
| FM 4 | contraponto / arpejo | musica (XGM2) | **NAO** |
| FM 5 | percussao tonal / stab | musica (XGM2) | **NAO** |
| FM 6 / DAC | usado pelo XGM2 para o mixer de PCM | driver XGM2 | **NAO** |
| PSG 1 | reforco de lead / brilho | musica (XGM2) | **NAO** |
| PSG 2 | arpejo rapido | musica (XGM2) | **NAO** |
| PSG 3 | baixo de apoio | musica (XGM2) | **NAO** |
| PSG noise | hi-hat / ruido | musica (XGM2) | **NAO** |
| **PCM 1** | PCM interno da musica | XGM2 | **NAO** — reservado |
| **PCM 2** | SFX critico | gameplay | sim, por prioridade |
| **PCM 3** | SFX ambiente / UI | gameplay | sim, por prioridade |

### 2.1 A resposta ao gate #5 do brief

O brief diz: "SFX nao rouba canal da musica sem regra em SOUNDMAP.md".

**Neste projeto SFX nunca rouba canal de musica. Nao por politica — por
arquitetura.** Com XGM2, todo SFX sai por PCM (canais 2 e 3), e FM/PSG pertencem
integralmente ao driver de musica. O gate e satisfeito por construcao.

`[DECIDIDO]` **Proibido** no codigo do jogo, herdado do prior art
(`audio_channel_ownership_report.json`, `forbidden_paths`):

- chamada direta a `PSG_*` enquanto o XGM2 esta carregado
- escrita direta em registro do YM2612
- uso de `SOUND_PCM_CH1` por qualquer SFX

Essas tres proibicoes sao verificaveis por grep no fonte. Viram gate em §6.

---

## 3. Politica de prioridade de SFX

`[VERIFICADO]` API: `XGM2_playPCMEx(sample, len, channel, priority)` com
prioridade 0-15 (`xgm2.h:200`). `XGM2_playPCM(...)` usa prioridade default 6.
`xgm2.h:160`: "default priority value of 6 which is below the minimum music PCM
priority (7)". Regra do driver: novo sample substitui o atual se
`nova prioridade >= antiga`.

`[DECIDIDO]` Faixas de prioridade deste projeto:

| Faixa | Uso | Canal | Exemplos |
|---|---|---|---|
| **15** | evento de estado irreversivel | PCM 2 | morte do Kirby, derrota do boss, vitoria de fase |
| **13** | dano recebido / dano no boss | PCM 2 | Kirby leva hit, boss leva hit |
| **11** | verbo do jogador | PCM 2 | inalar, engolir, cuspir estrela, ganhar habilidade |
| **9** | ataque de habilidade | PCM 3 | chama, beam, cutter, stone, sword |
| **7** | morte de inimigo | PCM 3 | inimigo estourando |
| **5** | movimento do jogador | PCM 3 | pulo, aterrissagem, passo de flutuar |
| **3** | ambiente / coleta | PCM 3 | item, cachoeira, bolha |
| **1** | UI | PCM 3 | cursor de menu |

### 3.1 O cenario de contencao, resolvido

"Kirby inalando enquanto 3 inimigos morrem no mesmo frame":

```
inalar          prioridade 11  ->  PCM 2   toca
morte inimigo A prioridade  7  ->  PCM 3   toca
morte inimigo B prioridade  7  ->  PCM 3 ja ocupado com prio 7; 7 >= 7 -> SUBSTITUI
morte inimigo C prioridade  7  ->  PCM 3 substitui de novo
```

Resultado audivel: o inalar (o verbo do jogador) sobrevive intacto, e as tres
mortes soam como **uma** morte. Isso e o comportamento correto: o jogador precisa
ouvir a propria acao, e "algo morreu" e informacao suficiente sobre o resto.

`[DECIDIDO]` **Regra anti-serrilhado:** morte de inimigo tem janela de supressao
de 4 frames. Segunda morte dentro de 4 frames **nao** re-disparra o sample. Sem
isso, 3 mortes em 3 frames produzem um estalo de sample cortado 3 vezes, que soa
como bug de audio.

### 3.2 Regra de nao-degradacao

`[DECIDIDO]` Prioridade **>= 11 nunca e descartada silenciosamente.** Se PCM 2
esta ocupado com prioridade >= 11 e chega outro >= 11, o novo entra em fila de 1
slot e toca no frame seguinte. Fila de 1, nao de N: audio atrasado mais de 1
frame do evento que o causou soa desconectado e e pior que audio perdido.

---

## 4. Orcamento de PCM em ROM

`[VERIFICADO]` 8 bits por sample, taxa fixa:

```
13.3 kHz  ->  13300 bytes por segundo
 6.65 kHz ->   6650 bytes por segundo
```

`[DECIDIDO]` Alocacao dentro do teto de 4 MB sem mapper:

| Bloco | Orcamento | % de 4 MB |
|---|---|---|
| Musica XGM2 compilada (8 faixas, FM+PSG) | 128 KB | 3.1% |
| Samples PCM | **384 KB** | 9.4% |
| Codigo + tiles + mapas | resto | — |

384 KB de PCM = **~29 segundos a 13.3 kHz**, ou ~58 s a 6.65 kHz, ou uma mistura.

### 4.1 Quem merece PCM, e quem nao merece

`[DECIDIDO]` PCM e o recurso de audio mais caro em ROM. Criterio: **so ganha PCM
o som que o FM nao consegue fazer com credibilidade.**

| Som | Rota | Taxa | Por que |
|---|---|---|---|
| Inalar (loop) | PCM | 6.65 kHz | ruido de sucção largo; FM nao faz ruido convincente |
| Engolir | PCM | 13.3 kHz | transiente curto e caracteristico |
| Bateria: kick | PCM | 13.3 kHz | punch de kick e a assinatura Koshiro; FM nao chega |
| Bateria: snare | PCM | 13.3 kHz | idem |
| Bateria: hi-hat | **PSG noise** | — | PSG faz hi-hat bem e de graca |
| Voz "Hi!" do Kirby | PCM | 13.3 kHz | e voz |
| Dano no Kirby | PCM | 13.3 kHz | precisa cortar a musica |
| Pulo | **FM** | — | FM faz blip melodico melhor e de graca |
| Coleta de item | **FM** | — | idem |
| Cursor de menu | **PSG** | — | idem |
| Chama (fire) | PCM | 6.65 kHz | ruido |
| Beam | **FM** | — | e tonal por natureza |
| Cutter | PCM | 13.3 kHz | swoosh metalico |
| Stone (impacto) | PCM | 13.3 kHz | impacto grave |
| Sword | PCM | 13.3 kHz | swoosh |

Contagem: 10 samples PCM. `[NAO MEDIDO]` custo real em bytes — depende da duracao
de cada um, que so existe depois da composicao.

---

## 5. A interacao com DMA — risco A4 do ARCHITECTURE.md

Este e o item de maior risco tecnico do subsistema.

### 5.1 O mecanismo

O Z80 executa o driver XGM2 e faz o mixing de PCM **inteiramente em software**
(`bin/rescomp.txt`: "100% running on Z80 cpu"). Durante um DMA do 68000 para a
VRAM, o Z80 fica impedido de acessar o bus. DMA pesado em VBlank **rouba tempo do
Z80** e o mixer perde amostras — o resultado audivel e engasgo ou estalo.

### 5.2 A restricao que o resto do codigo tem de obedecer

`[DECIDIDO]` Derivada do orcamento de [VRAMMAP.md](VRAMMAP.md) §3, que aloca
3176 dos 7372 bytes NTSC (43%) e deixa 57% de folga:

> **O DMA de um frame nao pode passar de 4096 bytes** (56% do teto de 7.2 KB).
> Os ~3.2 KB restantes ficam como margem para o Z80 nao ser estrangulado.

Isso e mais apertado que o teto do hardware **de proposito.** O teto de 7.2 KB e
o limite do VDP; o limite do audio e mais baixo e nao esta documentado em lugar
nenhum do SGDK. Na duvida, aperta-se.

`[NAO MEDIDO]` **Qual e o teto real de DMA antes do XGM2 engasgar.** Este e o
numero mais importante que falta no subsistema de audio.

Como medir: cena de teste tocando musica com PCM ativo, aumentando o DMA por
frame em passos de 512 bytes, monitorando `missed_frames` e `dma_wait` do driver
(o prior art ja expoe essas metricas) e ouvindo a captura. Para no primeiro
engasgo. **Enquanto isso nao existir, o teto de 4096 bytes fica.**

### 5.3 Ordem no frame

Do ARCHITECTURE.md §6.2, o passo 3 e "XGM tick", depois do DMA (passo 1) e do
`SPR_update` (passo 2). `[DECIDIDO]` Isso esta correto e nao muda: o driver roda
**depois** que o DMA do frame terminou, nao competindo com ele.

---

## 6. Ducking

`[DECIDIDO]` Ducking so existe porque escolhemos XGM2 (§1.1). Regra:

| Gatilho | Acao | Duracao |
|---|---|---|
| PCM prioridade >= 13 (dano, morte) | volume de FM e PSG para 50% | 12 frames, com rampa de volta em 8 |
| PCM prioridade 11 (verbo do jogador) | volume para 75% | 8 frames, rampa de 6 |
| PCM prioridade <= 9 | **sem ducking** | — |

Sem ducking abaixo de 9 porque duckar em ataque de habilidade — que dispara varias
vezes por segundo — faria a musica pulsar continuamente, o que soa como defeito.

`[NAO MEDIDO]` Se 50% e o valor certo. Precisa de ouvido humano, nao de script.

---

## 7. Gates — o que da e o que nao da para automatizar

Sendo honesto sobre o limite: **nenhum script julga se um baixo tem peso.**

### 7.1 Verificavel por automacao

| # | Gate | Como |
|---|---|---|
| A1 | Zero chamada direta a `PSG_*` no fonte do jogo | grep em `src/`, excluindo `audio/xgm_router.c` |
| A2 | Zero escrita direta em registro do YM2612 | grep por `YM2612_write` fora do router |
| A3 | Zero uso de `SOUND_PCM_CH1` em SFX | grep |
| A4 | Pico de DMA por frame <= 4096 bytes | **exige contador de DMA no probe** — mesmo blocker de VRAMMAP.md V6 |
| A5 | `missed_frames` do driver == 0 na cena mais pesada | probe precisa exportar a metrica do XGM2 |
| A6 | Orcamento de ROM de PCM <= 384 KB | somar tamanho dos samples no build |
| A7 | Toda faixa declarada em `res/resources.res` como `XGM2` | parse do `.res` |

A1-A3 e A7 sao implementaveis **hoje**, sem tocar no probe. A4 e A5 dependem de
instrumentacao.

### 7.2 Nao verificavel por automacao — exige ouvido humano

- se o baixo FM tem peso
- se o lead tem a doçura do Kirby sem soar fino
- se o kick de PCM tem punch
- se 50% de ducking e o valor certo
- se a trilha "e" Kirby

`[DECIDIDO]` Esses itens entram no gate de entrega como **checklist humano
assinado**, nao como script que finge julgar. Um `gates.py` que aprovasse
"qualidade musical" seria mentira automatizada.

---

## 8. Criterio de pronto do subsistema de audio

- [ ] A1-A3, A7 passando (grep + parse, implementavel hoje)
- [ ] A6 passando: PCM total <= 384 KB
- [ ] A4: pico de DMA <= 4096 B/frame — **exige probe instrumentado**
- [ ] A5: `missed_frames == 0` na cena mais pesada — **exige probe instrumentado**
- [ ] `[NAO MEDIDO]` teto real de DMA antes do engasgo, medido em degraus de 512 B
- [ ] zero roubo de canal FM/PSG por SFX — satisfeito por arquitetura, confirmar em captura
- [ ] cenario de contencao de 4 SFX simultaneos: o verbo do jogador sobrevive
- [ ] checklist humano de qualidade musical assinado
- [ ] DAC sem clip audivel na captura de audio do BlastEm

---

## 9. Changelog

| Data | Mudanca |
|---|---|
| 2026-07-29 | v1. **XGM2 escolhido** apesar de ter menos canais PCM (3 vs 4) e taxa menor (13.3 vs 14 kHz) que o XGM v1 — o fator decisivo e que so o XGM2 tem controle de volume de FM/PSG, sem o qual ducking nao existe. Brief corrigido: taxa e 13.3/6.65 kHz, nao 14-22 kHz. Propriedade de canal fechada: **SFX nunca rouba FM/PSG, por arquitetura**. 8 faixas de prioridade com supressao de 4 frames para morte de inimigo. Orcamento de PCM em 384 KB. Restricao de DMA imposta ao resto do codebase em 4096 B/frame (mais apertado que o teto do VDP, de proposito). 7 gates automatizaveis + checklist humano explicito para o que script nao julga. |
