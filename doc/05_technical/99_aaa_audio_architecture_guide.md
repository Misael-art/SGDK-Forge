# AAA Audio Architecture Guide — Mega Drive / Genesis

> O audio frequentemente separava um jogo mediano de uma superproducao. Este guia documenta as tecnicas AAA
> que estudios de alto nivel usavam para entregar reproducao cristalina de vozes digitalizadas (PCM) e efeitos
> sonoros complexos, contornando as limitacoes percebidas do hardware.

## 1. Hardware de Audio — Visao Completa

### YM2612 (FM Synthesis + DAC)

| Recurso | Especificacao |
|---------|--------------|
| Tipo | Yamaha OPN2 FM Synthesizer |
| Canais FM | 6 (CH1-CH6), 4 operadores por canal |
| DAC | 8-bit, substitui FM CH6 quando habilitado |
| Clock NTSC | 7,670,453 Hz |
| Clock PAL | 7,600,489 Hz |
| Rate Interno | Clock / 144 (~53 Khz) |

**O DAC e a porta de entrada para PCM.** Ao habilitar o DAC (registro 0x2B, bit 7), FM CH6 e silenciado e o registrador 0x2A aceita samples de 8-bit unsigned diretamente. Este e o mecanismo fundamental para toda reproducao de voz digitalizada no Mega Drive.

### SN76489 (PSG)

| Recurso | Especificacao |
|---------|--------------|
| Tipo | Texas Instruments SN76489 |
| Canais Tone | 3 (10-bit frequency, 4-bit attenuation) |
| Canal Noise | 1 (periodic ou white, 4-bit attenuation) |
| Clock | Compartilhado com Z80 (~3.58 MHz NTSC) |

**Subestimado para AAA.** PSG e excelente para: efeitos ambientais procedurais (vento, chuva via noise), bass drones (tone em frequencia baixa), beeps de UI sem custo ROM.

### Z80 — O Processador de Audio

| Recurso | Especificacao |
|---------|--------------|
| CPU | Zilog Z80A @ 3.579545 MHz (NTSC) |
| RAM | 8 KB (0x0000-0x1FFF) |
| Acesso YM2612 | Direto via 0x4000-0x4003 |
| Acesso PSG | Direto via 0x7F11 |
| Acesso ROM 68K | Via bank register (0x6000), janela 32KB em 0x8000-0xFFFF |
| Ciclos/Frame NTSC | ~59,659 |
| Ciclos/Frame PAL | ~70,937 |

**O Z80 e o coracao do audio.** Todo driver de audio roda no Z80. O 68K configura parametros e envia comandos; o Z80 faz o trabalho real de mixar canais, alimentar o DAC e controlar FM/PSG.

## 2. Por Que Audio "Abafado" Acontece

### Causas Raiz

1. **Sample rate muito baixo** — Abaixo de 8 Khz, frequencias altas (sibilantes: s, sh, ch) sao perdidas. Voz soa "dentro de uma lata".

2. **Formato inadequado** — 4-bit DPCM com pouca headroom gera artefatos em transientes. u-law e melhor para voz.

3. **Bus starvation** — VDP DMA pausa o Z80 completamente. Se DMA e heavy (muitos tiles por frame), o Z80 nao consegue alimentar o DAC a tempo → crackling, gaps.

4. **Clipping** — Sample normalizado sem headroom. Picos saturam o DAC em 0x00/0xFF → distorcao.

5. **DC offset** — Sample com media diferente de zero. Causa "estalo" no inicio/fim da reproducao.

6. **Falta de padding** — Sample nao alinhado a 256 bytes. Driver le lixo apos o sample → ruido.

### A Solucao AAA

Estudios como TENGEN (Gauntlet IV), Sega Technical Institute (Sonic 3), e Technosoft (Thunder Force IV) resolviam isso com:

1. **Drivers Z80 customizados** — Otimizados ciclo a ciclo para maximizar sample rate
2. **Double/triple buffering** — Previne gaps durante bank switch
3. **Bus protection** — Z80 sinaliza janelas seguras para DMA
4. **Pre-processamento rigoroso** — Samples convertidos com ferramentas profissionais
5. **ROM budget disciplinado** — Audio nao excedia 30-40% do ROM

## 3. Drivers de Audio SGDK 2.11

### Hierarquia de Drivers

```
Z80_DRIVER_XGM2 (5)     ← Padrao AAA. BGM sequenciado + 3 PCM @ 13.3 Khz.
Z80_DRIVER_XGM (4)      ← Legacy. BGM + 4 PCM @ 14 Khz.
Z80_DRIVER_PCM4 (3)     ← 4 canais PCM @ 16 Khz + volume 16 niveis.
Z80_DRIVER_DPCM2 (2)    ← 2 canais DPCM @ 22 Khz. Bom para SFX duplo.
Z80_DRIVER_PCM (1)      ← 1 canal, rate variavel 8-32 Khz. Maximo fidelidade single.
Z80_DRIVER_NULL (0)     ← Mudo. Libera Z80 para outros usos.
Z80_DRIVER_CUSTOM (-1)  ← Driver binario customizado via Z80_loadCustomDriver().
```

### Quando Usar Qual

| Cenario | Driver | Justificativa |
|---------|--------|--------------|
| Jogo completo (BGM + SFX + voz) | XGM2 | Padrao. Melhor balance geral |
| Cutscene com voz hi-fi | CUSTOM → XGM2 | Custom para voz, swap de volta para BGM |
| Demo tecnica de audio | PCM (single) | Maximo sample rate (32 Khz) |
| SFX intenso sem musica | PCM4 | 4 canais simultaneos com volume |
| Compressao maxima | DPCM2 | 50% ROM savings vs. PCM |

## 4. Streaming PCM — Arquitetura Ring Buffer

### Conceito

O Z80 tem apenas 8KB de RAM. Samples de voz podem ter 50-200KB. Solucao: streaming.

```
┌────────────────────────────────────────────────┐
│ 68K (Main CPU)                                  │
│ ┌──────────────────────────────────────────────┐│
│ │ ROM: [ sample data .... 100KB+ .... ]        ││
│ │       ^                                       ││
│ │       read_pos (avanca cada frame)            ││
│ └──────────────────────────────────────────────┘│
│         │ Z80_upload() cada VBlank               │
│         ▼                                        │
│ ┌──────────────────────────────────────────────┐│
│ │ Z80 RAM (8KB)                                 ││
│ │ [driver][vars][BufA 2KB][BufB 2KB][tables]   ││
│ │                  ▲          ▲                  ││
│ │           Z80 le aqui  68K escreve aqui       ││
│ └──────────────────────────────────────────────┘│
│         │                                        │
│         ▼                                        │
│ ┌──────────────────────────────────────────────┐│
│ │ YM2612 DAC (reg 0x2A)                        ││
│ │ Audio output → headphones/speakers            ││
│ └──────────────────────────────────────────────┘│
└────────────────────────────────────────────────┘
```

### Alimentacao: 68K → Z80

**VBlank Feed (simples):**
```c
void vblank_audio_feed(void) {
    if (!streaming) return;
    Z80_requestBus(TRUE);
    Z80_upload(inactive_buffer, &sample[pos], CHUNK);
    Z80_write(BUFFER_READY, 1);
    Z80_releaseBus();
    pos += CHUNK;
}
```

**Scatter Feed (AAA):**
Divide upload em 4 micro-chunks por frame. Menor contencao de BUS.

### Auto-Feed: Z80 → ROM

Z80 pode ler diretamente da janela bankeada (0x8000-0xFFFF):
```z80
LD HL, $8000 + offset   ; ROM bankeada
LD DE, buffer_dest       ; Z80 RAM
LD BC, chunk_size
LDIR                     ; block copy
```

Vantagem: 68K nao precisa intervir. Desvantagem: bank switch tem latencia.

## 5. Bus Contention — O Inimigo do Audio Limpo

### O Problema

```
Timeline de um frame NTSC:
├─── Active Display (192 linhas) ──────────┤── VBlank (28 linhas) ──┤
│ Z80 roda normalmente                     │ DMA pode pausar Z80!   │
│ (exceto durante 68K→Z80 RAM access)      │ Audio pode crackar     │
└──────────────────────────────────────────┴────────────────────────┘
```

Quando VDP DMA roda (upload de tiles, paleta, sprite table), o Z80 e **completamente pausado**. Se o Z80 estava no meio de alimentar o DAC, o sample para → crackling.

### Mitigacao AAA

1. **Z80_setBusProtection(true)** — Z80 escreve em endereco de sinal quando esta em ponto seguro. 68K so inicia DMA quando sinal esta ativo.

2. **Z80_setForceDelayDMA(true)** — Adiciona ~3 scanlines de atraso antes de DMA. Protege escrita PSG em andamento.

3. **Budget de DMA por frame** — Nunca fazer DMA de mais de X bytes por VBlank. Coordenar com `megadrive-vdp-budget-analyst`.

4. **Scatter DMA** — Distribuir transfers DMA ao longo de multiplos frames.

## 6. Qualidade de Sample — Pipeline de Preparacao

### Conversao

```bash
# Voz alta fidelidade (AAA)
sox input.wav -b 8 -e signed -r 13300 -c 1 -t raw output.raw

# SFX com compressao
sox input.wav -b 8 -e signed -r 8000 -c 1 -t raw output.raw

# Voz comprimida (ROM limitada)
sox input.wav -e u-law -r 13300 -c 1 -t raw output.raw
```

### Checklist de Qualidade

- [ ] Mono (MD nao tem stereo PCM real)
- [ ] Normalizado (dynamic range > 100)
- [ ] Sem DC offset (media proxima de zero)
- [ ] Sem clipping (< 1% de samples no limite)
- [ ] Alinhado a 256 bytes (silence padding no final)
- [ ] Loop points em zero-crossings (se looped)
- [ ] Testado com headphones
- [ ] Validado com `validate_audio.ps1`

### Validacao Automatizada

```powershell
# Na raiz do projeto:
powershell -File tools\sgdk_wrapper\validate_audio.ps1 -WorkDir .
# Com auto-fix de alinhamento:
powershell -File tools\sgdk_wrapper\validate_audio.ps1 -WorkDir . -Fix
# ROM de 2MB:
powershell -File tools\sgdk_wrapper\validate_audio.ps1 -WorkDir . -RomSizeKB 2048
```

Saida canonica:

- `out/logs/audio_validation_report.json`
- `out/logs/validate_audio_debug.log`
- `validation_report.json` deve absorver o estado do report de audio quando houver recursos declarados em `.res`

## 7. Nomenclatura de Assets de Audio

```
{tipo}_{nome}_{rate}khz_{bits}bit.{ext}

voice_announcer_round1_13k_8bit.raw
sfx_explosion_large_13k_8bit.raw
sfx_hit_punch_8k_8bit.raw
voice_boss_laugh_13k_ulaw.raw
ambient_wind_loop_8k_8bit.raw
```

## 8. Audio Architecture Card — Template Preenchido

### Exemplo: Beat 'em Up com Voz

```yaml
audio_surface_id: scene_stage1_gameplay
audio_role: "acao, recompensa, alerta, continuidade"
xgm2_mode: "bgm_sfx_ambience"

channel_ownership_map:
  FM_CH1-5: BGM (XGM2 sequencer)
  FM_CH6_DAC: BGM/PCM (XGM2 managed)
  PSG_CH1-3: BGM (XGM2 sequencer)
  PSG_NOISE: BGM
  PCM_CH1: SFX_COMBAT (priority 4-14)
  PCM_CH2: VOICE (priority 3-15)
  PCM_CH3: AMBIENT (priority 0-3, loop)

sfx_priority_table:
  15: voice_announcer, voice_boss
  14: sfx_death
  13: sfx_boss_cue
  11: sfx_explosion
  10: sfx_damage_taken
  9: sfx_hit_connect
  7: sfx_menu_select
  6: sfx_collect_item
  5: sfx_jump
  4: sfx_land, sfx_footstep
  3: typewriter_tick
  1: ambient_crowd, ambient_wind

music_stinger_plan:
  boss_intro: "fadeOut(30) → stinger 2s → boss BGM fadeIn(30)"
  stage_clear: "stop → victory jingle → silence"
  game_over: "stop → game over BGM"

audio_transition_plan:
  stage_to_boss: "BGM fadeOut → 30 frames silence → boss BGM fadeIn"
  gameplay_to_menu: "BGM fadeOutAndPause → menu silence"
  menu_to_gameplay: "BGM resume + fadeIn"

pause_resume_contract:
  pause: "XGM2_pause() + stopPCM(ALL) + save ambient state"
  resume: "XGM2_resume() + restart saved ambient loops"
  invariant: "NEVER leave orphan PCM playing after pause"

fallback_plan:
  channel_exhaustion: "Drop ambient (CH3) first, then secondary SFX"
  bus_contention: "Reduce DMA budget, enable bus protection"
  rom_budget: "Switch voice to DPCM, reduce ambient to PSG-only"
```

## 9. Integracao com Skills do Projeto

```
game-design-planning
    └→ Define audio requirements por cena
        └→ xgm2-audio-director
            └→ Desenha audio_architecture_card
            └→ Define channel_ownership_map
            └→ Coordena com z80-pcm-custom-driver (se AAA voice/effects)
                └→ Implementa driver customizado
                └→ Define bus_contention_analysis
                └→ Define rom_audio_budget
            └→ sgdk-runtime-coder
                └→ Implementa audio_director.c
                └→ Integra no main loop
                └→ Testa em BlastEm
            └→ megadrive-vdp-budget-analyst
                └→ Coordena DMA vs. audio bus contention
```

## 10. Referencia Rapida — APIs SGDK 2.11

### XGM2 (Driver Padrao)

```c
Z80_loadDriver(Z80_DRIVER_XGM2, TRUE);
XGM2_play(music_xgm2);
XGM2_playPCMEx(sample, len, SOUND_PCM_CH1, priority, halfRate, loop);
XGM2_stopPCM(SOUND_PCM_CH1);
XGM2_pause();
XGM2_resume();
XGM2_fadeOutAndStop(60);
XGM2_fadeIn(30);
XGM2_setFMVolume(80);
XGM2_setPSGVolume(60);
```

### Driver Customizado

```c
Z80_loadCustomDriver(my_driver_bin, my_driver_size);
Z80_requestBus(TRUE);
Z80_write(Z80_DRV_COMMAND, CMD_PLAY);
Z80_upload(Z80_DRV_PARAMS, sample_params, sizeof(params));
Z80_releaseBus();
```

### PSG Direto

```c
PSG_setFrequency(0, 440);      // Canal 0 = 440 Hz (La)
PSG_setEnvelope(0, 0);          // Volume maximo
PSG_setNoise(PSG_NOISE_TYPE_WHITE, PSG_NOISE_FREQ_CLOCK4);
PSG_setEnvelope(3, 5);          // Noise com volume medio
```

### Validacao de Audio

```c
bool playing = XGM2_isPlaying();
u8 pcm_state = XGM2_isPlayingPCM(SOUND_PCM_CH1_MSK | SOUND_PCM_CH2_MSK);
u16 cpu_load = XGM2_getCPULoad(TRUE);    // Media de Z80 CPU load
u16 dma_wait = XGM2_getDMAWaitTime(TRUE); // Tempo perdido em DMA
u8 missed = XGM2_getDebugMissedFrames();  // Frames com underrun
```
