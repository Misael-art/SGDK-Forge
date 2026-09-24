# 17 - Audio Design Document - __PROJECT_NAME__

Use este documento para decidir a identidade sonora, nao apenas listar arquivos.

## 1. Direcao Sonora

- Tom emocional: forja pesada, metal, calor. O golpe do martelo e o evento.
- Referencias tecnicas: YM2612 FM bed + PCM de impacto + PSG noise. Nao SNES.
- O que a musica deve fazer: segurar a oficina viva antes e depois do slam.
- O que os SFX precisam comunicar: o slam tem de parecer peso, nao whoosh.

## 2. Musica

| Faixa | Cena | Funcao | Escopo | Loop | Status | Evidencia |
|---|---|---|---|---|---|---|
| mus_forge_brand | branding + menu | cama FM da forja | micro_sketch_1m | restart via AUDIO_update | placeholder lab | ROM + BlastEm |

## 3. SFX

| SFX | Evento | Prioridade | Canal/driver | Risco de mascaramento | Evidencia |
|---|---|---|---|---|---|
| brand_hammer_slam | F120 contacto | 15 | XGM2 PCM CH2 + PSG noise/thump | BGM FM deve ceder o grave | sintetizado 13.3 kHz, placeholder |
| brand_stamp_whoosh | wordmark | 11 | PCM CH2 | nao compete com o slam | existente |

## 4. Integracao

- Driver:
- Politica de canais:
- Regras de ducking:
- Eventos reativos a beat:
- Fallbacks:

## 5. QA de Audio

- Sem clique em loop:
- SFX criticos audiveis:
- Audio OK em BlastEm:
- Evidencia:
