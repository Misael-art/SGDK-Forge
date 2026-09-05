# 17 — Audio Design Document — KIRBY_FAN GAME CLOUDE [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

> Contrato tecnico de audio: [SOUNDMAP.md](SOUNDMAP.md). Este documento e a
> direcao criativa e o pipeline de producao. Onde os dois divergirem, o
> SOUNDMAP manda.
> **Status:** `documentado`. Nenhuma nota foi ouvida rodando.

---

## 1. Direcao Sonora

### 1.1 O problema musical central

Kirby soa **brilhante, saltitante, em tom maior, muito melodico**. As referencias
de qualidade que o brief pede — Yuzo Koshiro em Streets of Rage 2, Motoaki
Takenouchi em Bloodlines — sao o oposto: graves, escuras, agressivas.

A tensao e real e precisa ser resolvida deliberadamente, nao no meio da
composicao:

> **Pegamos a ENGENHARIA de Koshiro e a MELODIA de Kirby.**
> Baixo FM com peso e presenca de sub, bateria PCM com punch, mixagem larga —
> mas servindo uma melodia doce em tom maior, nao um groove de rua.

- **Tom emocional:** doce, curioso, com energia de movimento. Perigo comunicado
  por ritmo e harmonia, nunca por escuridao — o mesmo principio da direcao visual.
- **Referencias tecnicas:** Koshiro (peso de baixo FM, punch de bateria),
  Takenouchi (uso de harmonia para atmosfera), ZPF e Xeno Crisis (teto atual do
  homebrew de MD).
- **O que a musica faz pela gameplay:** marca o ritmo de traversia. A faixa de
  fase e escrita no BPM que corresponde a cadencia de corrida do Kirby, para que
  correr sinta-se no tempo.
- **O que os SFX comunicam:** cada SFX carrega **uma** informacao de estado. SFX
  que nao carrega informacao nao entra no jogo.

### 1.2 O inimigo declarado: "FM fino"

Kirby mal executado no YM2612 vira caixinha de musica sem corpo. A cura **nao** e
adicionar notas — e dar peso ao baixo e punch a bateria, deixando a melodia leve
por cima de uma base solida. Toda revisao de faixa comeca perguntando "o baixo
sustenta isso?", nao "a melodia e bonita?".

### 1.3 Direcao por cena

| Cena | Tom | BPM | Instrumentacao | Funcao emocional |
|---|---|---|---|---|
| **Titulo** | Do maior | 96 | pad FM largo, lead com vibrato lento, sem bateria | calma, expectativa |
| **Vegetable Valley (f1)** | Sol maior | 138 | baixo FM saltitante, lead dobrado com PSG, kick+snare PCM, hi-hat PSG noise | alegria de movimento |
| **Lago (f2)** | Fa maior | 124 | baixo redondo, lead com portamento, arpejo PSG rapido | leveza aquosa |
| **Lago submerso** | Fa maior | 124 | **mesma faixa, filtrada**: PSG a 0, FM a 70% | abafamento, imersao |
| **Caverna (f3)** | La menor | 132 | baixo grave e sujo, lead reduzido, percussao seca | primeira tensao real |
| **Boss (Whispy)** | Re menor | 152 | baixo agressivo, stabs de FM, bateria cheia | urgencia comica |
| **Vitoria** | Sol maior | 120 | fanfarra curta, FM brilhante | recompensa |
| **Game over** | Do menor | 72 | 3 acordes descendentes, sem bateria | melancolia breve |

---

## 2. Musica

### 2.1 A faixa submersa e a MESMA faixa

`[DECIDIDO]` A fase 2 usa **uma** musica, nao duas. Ao cruzar a linha d'agua o
router muda o volume de PSG para 0 e o de FM para 70%. Isso e possivel **apenas**
porque escolhemos XGM2 (SOUNDMAP §1.1).

Custo em ROM: zero faixa adicional. Custo em CPU: uma escrita de volume.
Ganho: transicao instantanea e continua — a melodia nao reinicia quando o Kirby
entra na agua, que e o que uma troca de faixa faria.

Isso e **audio reagindo ao gameplay**, exigencia da FILOSOFIA MAXIMALISTA do
AGENTS.md, nao efeito decorativo.

### 2.2 Lista de faixas do VER.001

| Faixa | Cena | Funcao | Escopo | Loop | ROM alvo | Status |
|---|---|---|---|---|---|---|
| `mus_title` | titulo | expectativa | core_loop | sim, 32 s | 14 KB | `documentado` |
| `mus_stage_valley` | fase 1 | traversia alegre | modular_track | sim, 24 s | 18 KB | `documentado` |
| `mus_stage_lake` | fase 2 | leveza aquosa | modular_track | sim, 24 s | 18 KB | `documentado` |
| `mus_stage_cave` | fase 3 | tensao | modular_track | sim, 24 s | 18 KB | `documentado` |
| `mus_boss_whispy` | boss | urgencia | modular_track | sim, 20 s | 16 KB | `documentado` |
| `mus_victory` | pos-fase | recompensa | micro_sketch | nao, 6 s | 6 KB | `documentado` |
| `mus_gameover` | game over | melancolia | micro_sketch | nao, 8 s | 6 KB | `documentado` |
| `mus_ability_get` | copy ability | mudanca de estado | micro_sketch | nao, 2 s | 3 KB | `documentado` |
| | | | | **Total** | **99 KB** | |

Orcamento do SOUNDMAP §4: 128 KB. Folga de 29 KB.
`[NAO MEDIDO]` — tamanho real so existe depois do xgm2tool.

---

## 3. SFX

Prioridade e canal vem da tabela normativa do SOUNDMAP §3.

| SFX | Evento | Prio | Canal | Rota | O que comunica | Risco de mascaramento |
|---|---|---|---|---|---|---|
| `sfx_inhale_loop` | inalar mantido | 11 | PCM2 | PCM 6.65k | succao ativa e com alcance | baixo |
| `sfx_swallow` | engolir | 11 | PCM2 | PCM 13.3k | inimigo entrou, habilidade vem | baixo |
| `sfx_spit_star` | cuspir estrela | 11 | PCM2 | PCM 13.3k | projetil saiu | baixo |
| `sfx_ability_get` | ganhar ability | 11 | PCM2 | PCM 13.3k | seu moveset mudou | baixo |
| `sfx_kirby_hurt` | dano no Kirby | 13 | PCM2 | PCM 13.3k | perdeu vida | **ducka a musica** |
| `sfx_kirby_death` | morte | 15 | PCM2 | PCM 13.3k | fim de vida | ducka |
| `sfx_boss_hurt` | dano no boss | 13 | PCM2 | PCM 13.3k | acertou e contou | ducka |
| `sfx_boss_defeat` | boss derrotado | 15 | PCM2 | PCM 13.3k | fim de fase | ducka |
| `sfx_enemy_pop` | inimigo morre | 7 | PCM3 | PCM 13.3k | removido | **alto** — supressao de 4 frames |
| `sfx_jump` | pulo | 5 | PCM3 | FM | saiu do chao | medio |
| `sfx_float_puff` | puff de flutuar | 5 | PCM3 | FM | ganhou altura | **alto** — repete muito |
| `sfx_land` | aterrissar | 5 | PCM3 | FM | voltou ao chao | medio |
| `sfx_item` | coletar | 3 | PCM3 | FM | recompensa | baixo |
| `sfx_menu_move` | cursor | 1 | PCM3 | PSG | navegacao | baixo |
| `sfx_menu_ok` | confirmar | 1 | PCM3 | PSG | confirmacao | baixo |

**15 SFX: 10 em PCM, 5 sinteticos.** A regra do SOUNDMAP §4.1 decidiu cada rota —
so ganha PCM o som que o FM nao faz com credibilidade.

Os dois de risco alto sao os que repetem mais. `sfx_float_puff` dispara a cada
puff durante voo sustentado: precisa ser **curto e discreto**, ou vira metralhadora.

### 3.1 Identidade sonora das 5 copy abilities

Requisito: distinguiveis **de ouvido**, sem olhar a tela. Espelha o requisito
visual do R1-04, onde cada uma e distinguivel por forma alem de cor.

| Ability | Som | Rota | Prio | Carater |
|---|---|---|---|---|
| **FIRE** | rugido de chama, ruido largo, envelope longo | PCM 6.65k | 9 | continuo, quente |
| **BEAM** | zap descendente rapido, tonal | FM | 9 | eletrico, staccato |
| **CUTTER** | swoosh metalico com cauda | PCM 13.3k | 9 | agudo, cortante |
| **STONE** | impacto grave + rumor de poeira | PCM 13.3k | 9 | pesado, curto |
| **SWORD** | swoosh com corpo, mais grave que o cutter | PCM 13.3k | 9 | firme, decidido |

`[DECIDIDO]` CUTTER e SWORD sao os dois com maior chance de confusao. Separacao
deliberada: **CUTTER agudo com cauda longa, SWORD mais grave com corte seco.** Se
a revisao humana ainda confundir, SWORD ganha transiente metalico de ataque.

---

## 4. Integracao

- **Driver:** XGM2. Justificativa completa em SOUNDMAP §1 — resumo: e o unico com
  controle de volume de FM/PSG, sem o qual ducking nao existe. Escolhido apesar de
  ter menos canais PCM (3) e taxa menor (13.3 kHz) que o XGM v1 (4 a 14 kHz).
- **Politica de canais:** FM1-6 e PSG pertencem integralmente ao XGM2; PCM1 e
  reservado da musica; SFX vive em PCM2 e PCM3. **SFX nunca rouba canal de musica
  — por arquitetura, nao por politica.** Tabela normativa em SOUNDMAP §2.
- **Regras de ducking:** SOUNDMAP §6. Prio >= 13 -> FM/PSG a 50% por 12 frames;
  prio 11 -> 75% por 8 frames; prio <= 9 -> sem ducking, porque duckar em ataque
  de habilidade faria a musica pulsar continuamente.
- **Eventos reativos a beat:** nenhum no VER.001. `futuro_arquitetural` —
  sincronizar gimmick de fase ao beat exige o driver expor posicao de compasso, o
  que ainda nao foi verificado.
- **Fallbacks:** se `XGM2_playPCM` retornar FALSE (sem canal), SFX de prio <= 9 e
  descartado silenciosamente; prio >= 11 entra em fila de 1 slot (SOUNDMAP §3.2).

### 4.1 Pipeline de producao `[VERIFICADO]`

Ferramentas em `sdk/sgdk-2.11/bin/`: `xgm2tool.jar`, `xgmtool`,
`xgmRomBuilder.jar`, docs `xgm.txt` / `xgm2.txt`. `rescomp.jar` integra no build.

```
Furnace ou DefleMask
    |  exportar
    v
.vgm     <- YM2612 + SN76489 PSG. Musica APENAS.
    v
res/audio/<nome>.vgm     declarado no .res
```

Sintaxe de `bin/rescomp.txt`:

```
XGM2 name file [options]
```

Exemplo real deste projeto:

```
XGM2 mus_stage_valley audio/mus_stage_valley.vgm
```

Forma multi-track com PCM compartilhado:

```
XGM2 mus_stages audio/valley.vgm audio/lake.vgm audio/cave.vgm
```

`[DECIDIDO]` **Usar multi-track para as 3 fases.** Elas compartilham kick e
snare; declara-las juntas evita 3 copias dos mesmos samples em ROM. Chamadas por
`XGM2_playTrack(i)`.

### 4.2 O que o compositor entrega — requisitos duros

1. **Sistema alvo Mega Drive**, YM2612 + SN76489. Nenhum chip que o MD nao tem.
2. **Sem PCM na musica**, excecao unica: kick e snare, que vao no PCM1 reservado.
3. **Loop marcado** no ponto exato, sem clique na volta.
4. **PSG noise reservado para hi-hat.** Nao usar como canal tonal — herdado do
   prior art do workspace.
5. **No maximo 6 canais FM.** FM6 pertence ao mixer de PCM do XGM2.

Samples de SFX: **WAV mono 8-bit unsigned, 13300 Hz ou 6650 Hz.**

`[DECIDIDO]` Normalizar cada sample a **-3 dBFS de pico, nao 0 dBFS.** Margem para
o mixer somar 2 canais de PCM sem clipar o DAC. Dois samples a 0 dBFS tocando
juntos estouram.

### 4.3 Checklist de entrega do compositor

- [ ] `.vgm` toca no VGMPlay sem chip fora do MD
- [ ] loop no ponto certo, sem clique
- [ ] no maximo 6 canais FM, FM6 livre
- [ ] PSG noise so como hi-hat
- [ ] WAVs mono 8-bit em 13300 ou 6650 Hz
- [ ] todo WAV normalizado a -3 dBFS de pico
- [ ] duracao dentro do orcamento de §2.2

---

## 5. QA de Audio

Automatizavel (gates A1-A7 em SOUNDMAP §7.1):

- [ ] zero chamada direta a `PSG_*` fora do router — grep
- [ ] zero escrita direta em registro do YM2612 fora do router — grep
- [ ] zero uso de `SOUND_PCM_CH1` em SFX — grep
- [ ] toda faixa declarada como `XGM2` no `.res` — parse
- [ ] PCM total <= 384 KB — soma no build
- [ ] pico de DMA <= 4096 B/frame — **exige probe instrumentado**
- [ ] `missed_frames` do driver == 0 na cena mais pesada — **exige probe instrumentado**

### 5.1 O que so ouvido humano decide

Repetido de SOUNDMAP §7.2 porque e o item que mais se tenta burlar.

Nenhum script julga se o baixo tem peso, se o lead soa doce sem soar fino, se o
kick tem punch, se 50% de ducking e o valor certo, ou se a trilha "e" Kirby.

`[DECIDIDO]` Esses itens entram no gate de entrega como **checklist humano
assinado**, nao como script. Um gate automatizado que aprovasse "qualidade
musical" seria mentira automatizada.

- [ ] sem clique em loop — humano
- [ ] SFX criticos audiveis sob musica cheia — humano
- [ ] DAC sem clip com 2 PCM simultaneos — humano + captura de audio do BlastEm
- [ ] a trilha soa como Kirby, nao como Streets of Rage com melodia doce — humano
- [ ] evidencia: captura de audio do BlastEm por cena + assinatura humana

---

## 6. Changelog

| Data | Mudanca |
|---|---|
| 2026-07-29 | v1. Tensao central resolvida: engenharia de Koshiro, melodia de Kirby; inimigo declarado e o "FM fino". 8 faixas em 99 KB de 128. 15 SFX, 10 em PCM e 5 sinteticos, cada um com a informacao que carrega. Fase 2 usa UMA faixa com filtragem por volume na linha d'agua — possivel so por causa do XGM2. Identidade das 5 abilities com separacao deliberada CUTTER/SWORD. Pipeline `.vgm` -> rescomp `XGM2` verificado em `bin/rescomp.txt`; multi-track escolhido para as 3 fases. Normalizacao a -3 dBFS para nao clipar com 2 PCM somados. |
