# Sample Format Decision System — Mega Drive Audio AAA

Sistema de decisao para escolha de formato, sample rate, compressao e alocacao ROM de samples de audio.

## Decision Tree

```
PRECISO DE AUDIO PARA:
│
├─ BGM (musica de fundo)
│  └─ SEMPRE usar XGM2 format
│     - Eficiente (sequenced, nao raw PCM)
│     - ~10-50 KB por track (vs. MB em raw)
│     - Driver XGM2 ja faz playback otimizado
│     - SEM EXCECAO: BGM nunca em raw PCM
│
├─ Voz Digitalizada (speech, narration, announcer)
│  ├─ Qualidade maxima (ROM disponivel)
│  │  └─ 8-bit signed PCM @ 13.3+ Khz
│  │     - ~13.3 KB/segundo a 13.3 Khz
│  │     - Cristalina em headphones
│  │     - Custo: alto ROM usage
│  │
│  ├─ Qualidade boa (ROM limitada)
│  │  └─ u-law compressed @ 13.3 Khz
│  │     - Compressao logaritmica ideal para voz
│  │     - ~50% do espaco de raw PCM com qualidade comparavel
│  │     - Requer tabela de decode (256 bytes em Z80 RAM)
│  │
│  └─ Qualidade aceitavel (ROM critico)
│     └─ 4-bit DPCM @ 22 Khz (driver DPCM2)
│        - ~5.5 KB/segundo
│        - Artefatos visiveis em sibilantes (s, sh)
│        - OK para frases curtas de impacto
│
├─ SFX (explosao, impacto, UI)
│  ├─ Curto (<0.5s) e impactante
│  │  └─ 8-bit signed PCM @ 13.3 Khz
│  │     - ~6.6 KB por SFX de 0.5s
│  │     - Maximo impacto
│  │
│  ├─ Medio (0.5-2s)
│  │  └─ 8-bit signed PCM @ 8-11 Khz
│  │     - Reducao de rate aceitavel para SFX
│  │     - ~4-5.5 KB/segundo
│  │
│  └─ Loop continuo (motor, chuva, fogo)
│     └─ 8-bit signed PCM @ 8 Khz + loop point
│        - Sample curto (0.1-0.3s) em loop
│        - ~800 bytes - 2.4 KB
│        - Preparar loop em zero-crossing
│
├─ Ambiente (ambience, atmos)
│  └─ PSG direto (SN76489)
│     - Sem custo ROM (gerado proceduralmente)
│     - Noise channel para vento, chuva
│     - Tone channels para drones, hum
│     - Combinar com PCM SFX para camada
│
└─ Efeito Especial (echo, reverb, stinger)
   └─ Z80 DSP (processamento no driver)
      - Echo: delay line em Z80 RAM (~256 bytes)
      - Pitch: accumulator-based rate change
      - Volume: lookup table (4KB se PCM4-style)
      - Sem custo ROM adicional
```

## Sample Rate Selection Matrix

| Rate (Khz) | Qualidade | Z80 Cycles/Sample | Uso Ideal | ROM Cost/sec |
|-------------|-----------|-------------------|-----------|--------------|
| 32.0 | Excelente | 112 | Voice-only driver (single channel) | 32 KB |
| 22.05 | Muito Boa | 162 | DPCM 2-channel | 11 KB (DPCM) |
| 16.0 | Boa | 224 | Multi-channel SFX (PCM4) | 16 KB |
| 13.3 | Padrao AAA | 269 | XGM2 BGM+PCM, voice, SFX | 13.3 KB |
| 11.025 | Aceitavel | 325 | SFX medio, voice comprimida | 11 KB |
| 8.0 | Minima | 447 | Loops ambientais, SFX simples | 8 KB |

**Regra de ouro:** Abaixo de 8 Khz, voz SEMPRE soa abafada. NAO usar.

## ROM Budget Allocation

### Template de Alocacao (ROM 4MB)

```
ROM Total:          4,194,304 bytes (4 MB)

Codigo 68K:           512,000 bytes (12%)
Tiles/Sprites:      1,400,000 bytes (33%)
Maps/Tilemaps:        400,000 bytes (10%)
BGM (XGM2):           200,000 bytes (5%)
PCM Samples:          800,000 bytes (19%)  ← AUDIO BUDGET
Paletas/Misc:         100,000 bytes (2%)
Reserva:              782,304 bytes (19%)

Audio Total:        1,000,000 bytes (24%)  ← BGM + PCM
```

### Template de Alocacao (ROM 2MB)

```
ROM Total:          2,097,152 bytes (2 MB)

Codigo 68K:           300,000 bytes (14%)
Tiles/Sprites:        800,000 bytes (38%)
Maps/Tilemaps:        250,000 bytes (12%)
BGM (XGM2):           100,000 bytes (5%)
PCM Samples:          350,000 bytes (17%)  ← AUDIO BUDGET
Paletas/Misc:          50,000 bytes (2%)
Reserva:              247,152 bytes (12%)

Audio Total:          450,000 bytes (22%)  ← BGM + PCM
```

### Regra dos 40%

Audio total (BGM + PCM) NAO deve exceder 40% do ROM.
Sinal de alerta a 30%. Redesign obrigatorio acima de 40%.

## Format Comparison Table

| Formato | Bits/Sample | Qualidade Voz | Qualidade SFX | ROM Efficiency | Z80 Decode Cost |
|---------|-------------|---------------|---------------|----------------|-----------------|
| 8-bit signed PCM | 8 | Excelente | Excelente | 1x (baseline) | 0 (direct output) |
| 4-bit DPCM | 4 | Boa | Boa | 2x savings | ~10 cycles |
| u-law | 8 (compressed) | Muito Boa | Boa | ~1.5-2x effective | ~5 cycles (table lookup) |
| 4-bit ADPCM (IMA) | 4 | Boa+ | Boa | 2x savings | ~15-20 cycles |
| 1-bit delta | 1 | Ruim | Ruim | 8x savings | ~3 cycles |

## Sample Preparation Checklist

### Pre-Integracao (OBRIGATORIO)

- [ ] Source audio em 16-bit WAV ou superior
- [ ] Convertido para mono (Mega Drive nao tem stereo PCM real)
- [ ] Sample rate escolhido conforme decision tree acima
- [ ] Convertido para formato alvo (8-bit signed, DPCM, u-law)
- [ ] Normalizado para usar dynamic range completo (-128 a 127)
- [ ] Silence trimmed no inicio (nao no final — padding necessario)
- [ ] Final padded com silence ate proximo multiplo de 256 bytes (128 para DPCM)
- [ ] Loop points em zero-crossings (se sample e looped)
- [ ] Crossfade aplicado em loop boundary (4-8 samples)
- [ ] Testado com headphones para artefatos (cliques, pops, distorcao)
- [ ] Tamanho registrado na tabela de ROM budget

### Ferramentas Recomendadas

| Ferramenta | Uso | Comando Exemplo |
|------------|-----|-----------------|
| SoX | Conversao de formato, rate, normalize | `sox in.wav -b 8 -e signed -r 13300 -c 1 out.raw` |
| Audacity | Edicao visual, loop point, normalize | Export → Raw (signed 8-bit) |
| ffmpeg | Conversao batch, extração de audio | `ffmpeg -i in.mp3 -ar 13300 -ac 1 -f s8 out.raw` |
| Python | Padding, alignment, analysis | Script customizado (ver abaixo) |

### Script de Validacao (Python)

```python
import struct
import os
import sys

def validate_sample(filepath, alignment=256):
    size = os.path.getsize(filepath)

    issues = []

    # Check alignment
    if size % alignment != 0:
        issues.append(f"NOT ALIGNED: {size} bytes, needs {alignment - (size % alignment)} padding")

    # Check for DC offset
    with open(filepath, 'rb') as f:
        data = f.read()

    samples = struct.unpack(f'{len(data)}b', data)  # signed bytes
    avg = sum(samples) / len(samples)
    if abs(avg) > 5:
        issues.append(f"DC OFFSET: average = {avg:.1f} (should be near 0)")

    # Check dynamic range
    min_val = min(samples)
    max_val = max(samples)
    dynamic_range = max_val - min_val
    if dynamic_range < 100:
        issues.append(f"LOW DYNAMIC RANGE: {dynamic_range} (should be >100 for clarity)")

    # Check for clipping
    clip_count = sum(1 for s in samples if s == 127 or s == -128)
    clip_pct = clip_count / len(samples) * 100
    if clip_pct > 1:
        issues.append(f"CLIPPING: {clip_pct:.1f}% of samples at limits")

    # Check loop point (last 256 bytes should end near zero)
    tail = samples[-8:]
    tail_avg = sum(abs(s) for s in tail) / len(tail)
    if tail_avg > 20:
        issues.append(f"LOOP RISK: tail average amplitude = {tail_avg:.1f} (may click at loop)")

    # Report
    print(f"Sample: {filepath}")
    print(f"  Size: {size} bytes ({size/1024:.1f} KB)")
    print(f"  Duration: {size/13300:.2f}s at 13.3Khz")
    print(f"  Range: [{min_val}, {max_val}] (dynamic: {dynamic_range})")

    if issues:
        print(f"  ISSUES ({len(issues)}):")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("  STATUS: PASS")

    return len(issues) == 0
```

## Nomenclatura de Samples

Pattern obrigatorio para samples no projeto:

```
{tipo}_{nome}_{rate}khz_{bits}bit.{ext}

Exemplos:
  voice_announcer_round1_13k_8bit.raw
  sfx_explosion_large_13k_8bit.raw
  sfx_hit_punch_8k_8bit.raw
  voice_boss_laugh_13k_ulaw.raw
  ambient_wind_loop_8k_8bit.raw
```

Campos:
- `tipo`: voice, sfx, ambient, stinger
- `nome`: descritivo (snake_case)
- `rate`: sample rate em Khz (8k, 11k, 13k, 16k, 22k, 32k)
- `bits`: formato (8bit, 4bit, ulaw, dpcm)
- `ext`: raw (uncompressed), dpcm (delta coded), bin (custom)
