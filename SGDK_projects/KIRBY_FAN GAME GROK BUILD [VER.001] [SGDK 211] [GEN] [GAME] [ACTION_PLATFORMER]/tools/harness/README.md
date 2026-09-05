# tools/harness — o que cada gate prova, e o que NAO prova

> Leia isto antes de confiar num run verde. Vários gates aqui sao invariantes
> estruturais que **nao podem falhar por construcao**: eles existem como canario
> de corrupcao, nao como prova de que o orcamento foi respeitado.

---

## Como rodar

```bash
# build (unica rota funcional neste host Linux)
bash ../../tools/sgdk_wrapper/build_sgdk_wine_bridge.sh --project-root "$PWD"

# cenas: 4 = STAGE  5 = STAGE_PLAYTEST  6 = BOSS  7 = BOSS_PLAYTEST
#        8 = GAMEOVER  9 = TITLE (boot default)
#
# O playtest roda na cena 5. Nela a camera fica parada, entao o gate de parallax
# passa VACUAMENTE e avisa: quem prova parallax e a captura da cena 4.
bash ../../tools/sgdk_wrapper/capture_blastem_evidence_linux.sh \
    --project-root "$PWD" \
    --output-base "$PWD/out/evidence/<nome>" \
    --target-scene 4 --warmup-seconds 13

# gates de runtime sobre o bundle selado
python3 tools/harness/gates.py out/evidence/<nome>/<session>/

# gates estaticos de audio (nao precisam de ROM rodando)
python3 tools/harness/audio_gates.py
```

Se a captura der `reason=window_timeout` com `blastem.log` de 0 bytes, o bloqueio
quase sempre e uma **instancia flatpak presa da execucao anterior**:

```bash
flatpak ps          # <-- olhe AQUI primeiro; nao aparece em `ps -eo comm`
ps -eo pid,comm | grep blast
```

Medido em 2026-08-06, apos cinco falhas seguidas: os processos `blastem.bin`
**sobrevivem ao `flatpak kill`** e nao aparecem de forma confiavel em
`flatpak ps`. Eles se acumulam a cada captura falha e pioram o problema.

A limpeza que de fato funciona, e que vale rodar ANTES de uma serie de capturas:

```bash
for p in $(ps -eo pid,comm | awk '$2 ~ /^blastem/ {print $1}'); do kill -9 "$p"; done
```

Nunca `pkill -f blastem`: o padrao casa com o proprio comando do agente.

---

## Os arquivos

| Arquivo | Papel |
|---|---|
| `gates.py` | gates de runtime sobre um bundle selado. Exit != 0 em violacao |
| `probe_format.py` | leitor do bloco canonico VLAB (metricas + 64 cores de CRAM) |
| `krb1.py` | leitor do bloco **proprio** do projeto, KRB1 em SRAM 0x300 |
| `../../src/system/playtest.c` | script de input gravado, do lado da ROM (nao e do harness, mas e o que alimenta os dois gates de playtest) |
| `frametime.py` | p50/p95/p99 das amostras de CPU load do bloco MDRT |
| `audio_gates.py` | gates estaticos do contrato de audio (grep + parse do `.res`) |
| `audio_gate_baseline.json` | divida herdada do template, rastreada e nao silenciada |

**Por que dois blocos de telemetria:** o selador canonico
`tools/sgdk_wrapper/seal_fresh_evidence_bundle.py` define VLAB como
"words[0..23] sao metricas, words[24..] sao as 64 entradas de CRAM".
Acrescentar metrica ao VLAB deslocaria a paleta e corromperia todos os gates de
cor do workspace. Esse selador e canonico e AGENTS.md proibe alterar sem
aprovacao humana. Entao o projeto emite o proprio bloco. Detalhes em
`inc/system/probe_stage.h`.

---

## Gates que PODEM falhar de verdade

| Gate | Prova | Nao prova |
|---|---|---|
| `scene_identity` | a captura mostra a cena pedida | nada sobre qualidade |
| **`music_audible`** (A8) | RMS acima do piso de silencio MEDIDO com a musica desligada | que a musica e boa; so que sai som |
| **`dac_headroom`** (A9) | pico com folga para PCM simultaneo | — |
| `sprites_per_frame` | pico medido de sprites de hardware | que o pico foi atingido na cena mais pesada |
| `sprites_per_scanline` | pico numa scanline **amostrada** | e AMOSTRADO: 4 scanlines por frame, nao exaustivo |
| `plane_size_locked` | plano e 64x32 | — |
| `vram_tile_budget` | uso declarado cabe abaixo de 0xC000 | uso REAL de tile; le o numero declarado em `doc/VRAMMAP.md` |
| `zero_over_budget_frames` | 0 frames acima do budget na janela | performance sustentada: a janela e de 32 amostras |
| `cpu_load_p99` | p99 na janela de 32 amostras | idem |
| **`parallax_layer_speeds`** | as 4 camadas conferem com a formula de projeto, lido da tabela de HScroll que a ROM programou | que a camera estava em movimento — ver `parallax_camera_moved` |
| **`tile_priority_under_sh`** | nenhum tile de fundo em prioridade 0 nas entradas amostradas | e AMOSTRADO: 16 entradas por plano, passo de 2 linhas |
| **`dma_peak_per_frame`** | pico de bytes enfileirados por frame | que o pico coincide com o frame mais pesado |
| **`playtest_coverage`** | os 11 estados do jogador foram ALCANCADOS, observados pela cena | que o game feel e bom; so que o estado ocorreu |
| **`playtest_completed`** | o script gravado chegou ao fim | — |
| `pcm_rom_budget` (audio) | soma real dos samples em disco | — |
| `no_direct_psg_calls` etc. | ausencia dos padroes proibidos no fonte | divida herdada esta em baseline, ver abaixo |

---

## Gates que NAO podem falhar por construcao

Mantidos como canario de corrupcao. Um verde aqui **nao** e verificacao independente.

- **`color_budget`** — sao 60 slots nao transparentes + 1 backdrop, logo a contagem
  nunca passa de 61 e o teto e 58. Falhar aqui significa dump malformado, nao
  arte gastando cor demais.
- **`cram_rgb333_legal`** — `PAL_getColors()` mascara cada entrada com
  `VDPPALETTE_COLORMASK` (0x0EEE) ao ler o CRAM, entao valor ilegal nao chega ao
  dump por esse caminho.
- **`vram_tables_in_range` / `vram_tables_disjoint`** — os enderecos vem dos
  defaults do SGDK e sao disjuntos por definicao ate alguem chamar
  `VDP_setBGAAddress` e amigos.
- **`screenshot_color_count`** — REBAIXADO A SOFT em 2026-08-06. O teto era
  "entradas de CRAM uteis x 3" por causa do S/H, e esse modelo **quebra com
  raster**: o gradiente de ceu percorre UMA entrada de CRAM por 12 stops no mesmo
  frame, rendendo ate 36 cores de tela sozinha. Medido 262 numa cena correta
  contra o teto modelado de 174. A restricao real e ocupacao de CRAM, coberta por
  `color_budget`.

---

## Armadilhas medidas, nao teoricas

1. **Cor de screenshot nao e cor de CRAM.** O BlastEm converte 9 bits para RGB
   com curva de DAC realista, nao `n*255/7`. Medimos `(119,87,49)` onde a paleta
   tem `(109,73,36)`. **Nunca** verificar legalidade RGB333 pelo PNG.
2. **`screenshot_color_count` tem teto 174, nao 58.** Com Shadow/Highlight global,
   cada cor de CRAM pode aparecer normal, sombreada e clareada no mesmo frame.
   58 aqui reprovaria toda cena real.
3. **`shadow_highlight_intent` e soft e prova INTENCAO.** SGDK 2.11 nao expoe
   leitura do registro 0x0C. E copia-sombra do que a ROM pediu.
4. **Gate amostrado com denominador 0 e vacuo, nao aprovado.** Por isso
   `tile_priority_under_sh` e `parallax_camera_moved` emitem aviso explicito
   quando o denominador e zero ou a camera esta parada. Um gate que le "0 de 0"
   ja foi confundido com aprovacao neste projeto.
5. **A secao `sprite` da atribuicao por scanline nao e custo por sprite.** Medido:
   104 com 5 sprites, 53 com 25, 43 com 9. E pico ruidoso. O que escala e
   `cpu_load_p99`.

---

## O que continua sem gate nenhum

- **Qualidade musical.** Nenhum script julga se o baixo tem peso ou se o kick tem
  punch. Isso e checklist humano assinado (`doc/SOUNDMAP.md` §7.2). Um gate que
  aprovasse "qualidade musical" seria mentira automatizada.
- **`missed_frames` do driver XGM2** (gate A5) — o audio TOCA desde 2026-08-06 e
  os gates A8/A9 provam que sai som com folga de DAC, mas o probe ainda nao
  exporta as metricas internas do driver, entao engasgo por DMA continua sem gate.
- **Game feel.** O playtest prova que um estado foi ALCANCADO, nunca que a
  fisica e boa. Coyote time, hit-stop e arco de knockback continuam sem
  julgamento automatizado — e nao devem ganhar um.
- **Performance sustentada.** Toda janela de CPU tem 32 amostras. Nada aqui prova
  60 fps por minutos.

---

## Baseline de audio

`audio_gate_baseline.json` lista 11 violacoes **herdadas do template**
(`src/system/audio.c`, `src/scenes/scene_branding.c`). Baseline **nao e isencao**:
o gate falha em qualquer violacao NOVA e reporta a herdada como warning com owner
e condicao de expiracao, LIDA do proprio arquivo em vez de repetida no codigo.

A condicao original dizia "quando `xgm_router.c` existir". Ele existe desde
2026-08-06 e **a divida nao zerou**: as violacoes vivem nas cenas do TEMPLATE
(branding/menu/demo), que hoje estao INALCANCAVEIS mas cujos ARQUIVOS seguem em
`src/` — e o gate faz grep em arquivo, nao em codigo alcancavel. A condicao real
existir. Verificado injetando uma violacao nova: o gate falhou corretamente.
