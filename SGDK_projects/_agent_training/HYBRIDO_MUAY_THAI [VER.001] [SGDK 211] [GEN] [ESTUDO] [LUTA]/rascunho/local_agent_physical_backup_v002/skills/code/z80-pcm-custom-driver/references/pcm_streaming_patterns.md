# PCM Streaming Patterns — Mega Drive AAA Audio

Reference para implementacao de streaming PCM de alta qualidade no Z80.

## 1. Ring Buffer Architecture

### Double Buffer (Padrao Minimo)

```
Z80 RAM Layout:
0x0000-0x00FF  Driver code + vars
0x0100-0x0104  Command/Status/Params (protocolo SGDK)
0x0105-0x01FF  Driver vars + lookup tables
0x0200-0x09FF  Buffer A (2KB)
0x0A00-0x11FF  Buffer B (2KB)
0x1200-0x1FFF  Remaining space (volume tables, etc.)
```

**Fluxo:**
1. 68K preenche Buffer A via Z80 RAM write (requer BUS)
2. Z80 reproduz Buffer A enquanto 68K preenche Buffer B
3. Swap: Z80 comeca Buffer B, 68K preenche Buffer A
4. Repeat

**Tamanho de buffer por frame (NTSC 60fps):**
- 8 Khz: 133 bytes/frame
- 13.3 Khz: 222 bytes/frame
- 16 Khz: 267 bytes/frame
- 22 Khz: 367 bytes/frame

### Triple Buffer (Recomendado AAA)

Adiciona terceiro buffer para absorver jitter de DMA:

```
Buffer A: 0x0200-0x07FF  (1.5KB)
Buffer B: 0x0800-0x0DFF  (1.5KB)
Buffer C: 0x0E00-0x13FF  (1.5KB)
```

**Vantagem:** Se um frame de 68K atrasa por DMA heavy, ainda sobra um buffer inteiro de margem.

## 2. Bank Switching para Samples Grandes

Samples maiores que 32KB requerem bank switching:

```
68K Side (C / SGDK):
1. Z80_requestBus(TRUE)
2. Z80_setBank(sample_addr >> 15)
3. Write sample offset + length to Z80 params
4. Write PLAY command
5. Z80_releaseBus()

Z80 Side:
1. Read params (bank-relative offset, length)
2. Access sample at 0x8000 + offset
3. When reaching end of 32KB window:
   a. Pause output briefly
   b. Update bank register (9 serial writes to 0x6000)
   c. Reset read pointer to 0x8000
   d. Resume output
```

**Custo do bank switch:** ~45 Z80 cycles (9 writes x 5 cycles each) + setup = ~60-80 cycles total.

**Mitigacao:** Pre-fetch proximos bytes antes do boundary para evitar gap audivel.

## 3. Alimentacao pelo 68K (Feed Patterns)

### Pattern A: VBlank Feed (Simples)

```c
// No VBlank callback do 68K:
void audio_vblank_feed(void) {
    if (!audio_streaming) return;

    Z80_requestBus(TRUE);
    // Upload next chunk to inactive buffer
    Z80_upload(next_buffer_addr, &sample_data[sample_pos], CHUNK_SIZE);
    // Signal Z80 that buffer is ready
    Z80_write(BUFFER_READY_FLAG, 1);
    Z80_releaseBus();

    sample_pos += CHUNK_SIZE;
    if (sample_pos >= sample_len) {
        if (looping) sample_pos = loop_point;
        else audio_streaming = FALSE;
    }
}
```

**Limitacao:** VBlank time e disputado com DMA de tiles/sprites.

### Pattern B: Scatter Feed (AAA)

Divide upload em chunks menores distribuidos pelo frame:

```c
// Chamar multiplas vezes por frame (e.g., 4x)
void audio_scatter_feed(void) {
    if (chunks_remaining <= 0) return;

    Z80_requestBus(TRUE);
    Z80_upload(buffer_write_pos, &sample_data[sample_pos], MICRO_CHUNK);
    Z80_releaseBus();

    buffer_write_pos += MICRO_CHUNK;
    sample_pos += MICRO_CHUNK;
    chunks_remaining--;
}
```

**Vantagem:** Menor contencao de BUS. Z80 pausa por menos tempo em cada acesso.

### Pattern C: Z80 Self-Feed from ROM (Avancado)

Z80 le diretamente da janela de ROM bankeada:

```z80
; Z80 reads sample directly from banked ROM
feed_from_rom:
    LD HL, $8000 + sample_offset  ; banked ROM address
    LD DE, buffer_write            ; Z80 RAM dest
    LD BC, chunk_size
    LDIR                           ; block copy
    RET
```

**Vantagem:** Nao precisa de 68K para alimentar — Z80 e autonomo.
**Limitacao:** Bank switch tem custo, e Z80 nao pode acessar ROM durante 68K DMA (bus halt).

## 4. Underrun Detection e Recovery

```z80
; Z80 checks if read pointer caught up to write pointer
check_underrun:
    LD A, (read_pos_high)
    LD B, A
    LD A, (write_pos_high)
    CP B
    JR NZ, .no_underrun
    ; Underrun! Output silence
    LD A, $80              ; DAC center (silence)
    LD ($4000), A          ; YM2612 addr = DAC register
    LD ($4001), A          ; Write silence
    ; Set underrun flag for 68K to detect
    LD A, (STATUS)
    OR $40                 ; bit 6 = underrun flag
    LD (STATUS), A
    RET
.no_underrun:
    ; Normal playback continues
    RET
```

**Regra AAA:** Silence e melhor que lixo. Underrun produz um breve silencio em vez de crackling.

## 5. Sample Pre-processing Pipeline

### Conversao de Formato

| Source | Target | Ferramenta | Comando |
|--------|--------|------------|---------|
| WAV 16-bit | 8-bit signed PCM | SoX | `sox input.wav -b 8 -e signed -r 13300 output.raw` |
| WAV 16-bit | 4-bit DPCM | Custom encoder | Encode deltas, pack 2 samples/byte |
| MP3/OGG | 8-bit signed PCM | SoX | `sox input.mp3 -b 8 -e signed -r 13300 -c 1 output.raw` |
| Any | u-law compressed | SoX | `sox input.wav -e u-law -r 13300 -c 1 output.raw` |

### Alinhamento

```python
# Pad sample to 256-byte boundary
import os
sample_size = os.path.getsize("sample.raw")
padding = (256 - (sample_size % 256)) % 256
with open("sample.raw", "ab") as f:
    f.write(b'\x80' * padding)  # silence padding (0x80 = center for unsigned)
```

### Loop Point Preparation

1. Identificar zero-crossing mais proximo do loop point desejado
2. Adicionar 4-8 samples de crossfade entre fim e inicio
3. Garantir que loop boundary caia em alinhamento de 256 bytes
4. Testar com headphones para cliques

## 6. Mixing de Multiplos Canais no Z80

### Mixing por Soma com Clipping

```z80
; Mix 2 channels (signed 8-bit) into DAC output
mix_2ch:
    LD A, (ch1_sample)      ; channel 1 sample (signed)
    LD B, A
    LD A, (ch2_sample)      ; channel 2 sample (signed)
    ADD A, B                ; sum
    ; Clipping check
    JP PO, .no_overflow     ; parity overflow flag = signed overflow
    JP P, .clip_neg
    LD A, $7F               ; positive clip
    JR .output
.clip_neg:
    LD A, $80               ; negative clip
    JR .output
.no_overflow:
    SRA A                   ; divide by 2 to prevent overall clipping
.output:
    ADD A, $80              ; convert to unsigned for DAC
    LD ($4001), A           ; output to DAC
    RET
```

**Custo:** ~30-40 Z80 cycles per mixed sample (2 channels).

### Mixing com Volume Table (PCM4 Pattern)

```
Volume table: 256 entries x 16 volume levels = 4096 bytes
Location: Z80 RAM $1000-$1FFF (se caber)

Lookup: output = volume_table[volume_level * 256 + sample_value]
```

**Vantagem:** Volume por canal sem multiplicacao.
**Custo:** 4KB de Z80 RAM — so viavel com driver compacto.

## 7. Prioridade e Preempcao de Canais

```
Priority System (XGM2 compatible):
Level 0-3:   Ambient/background (interruptible)
Level 4-7:   Standard SFX (player actions)
Level 8-11:  Important SFX (damage, collectibles)
Level 12-14: Critical SFX (boss cues, alerts)
Level 15:    Voice/cinematic (maximum priority)

Rule: Higher priority ALWAYS preempts lower.
Rule: Same priority = newest wins.
Rule: BGM channels are NEVER preempted by SFX (separate ownership).
```

## 8. Efeitos Avancados no Z80

### Echo Simulado

```z80
; Simple delay-line echo (cost: ~15 cycles + buffer RAM)
echo_process:
    LD A, (current_sample)
    LD B, A                    ; B = dry signal
    LD HL, echo_buffer
    LD D, (HL)                 ; D = delayed sample
    LD (HL), A                 ; store current in delay line
    ; Mix: output = dry * 0.75 + wet * 0.25
    SRA D                      ; wet / 2
    SRA D                      ; wet / 4
    ADD A, D                   ; dry + wet/4
    ; Advance delay pointer (circular)
    INC L                      ; assumes 256-byte aligned buffer
    LD (echo_ptr_low), A
    RET
```

**Custo:** ~256 bytes RAM para ~19ms echo a 13.3 Khz.

### Pitch Shifting (Variable Rate Playback)

```z80
; Accumulator-based pitch control
; pitch_inc: 8.8 fixed point (0x0100 = normal speed)
pitch_advance:
    LD HL, (pitch_accumulator)
    LD DE, (pitch_inc)
    ADD HL, DE
    LD (pitch_accumulator), HL
    ; H = integer part = number of source samples to skip
    LD A, H
    LD (skip_count), A
    LD H, 0                    ; keep only fractional part
    LD (pitch_accumulator), HL
    RET
```
