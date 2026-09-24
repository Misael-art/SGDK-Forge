# 17 - Audio Design Document - HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]

Use este documento para decidir a identidade sonora, nao apenas listar arquivos.

## 1. Direcao Sonora

- Tom emocional: forja pesada, metal, calor. O golpe do martelo e o evento.
- Referencias tecnicas: driver XGM SGDK 2.11, PSG cristalino para o tema e PCM
  separado para os golpes. Nao SNES.
- O que a musica deve fazer: segurar a oficina viva antes e depois do slam.
- O que os SFX precisam comunicar: o slam tem de parecer peso, nao whoosh.

## 2. Musica

| Faixa | Cena | Funcao | Escopo | Loop | Status | Evidencia |
|---|---|---|---|---|---|---|
| mus_forge_brand / Forge Crystal | luta + Sound Test | identidade autoral de forja; lead, baixo, contraponto cristalino e percussao PSG | 8 compassos, 150 BPM, 4/4, A menor | loop VGM/XGM deterministico, 12,8 s | candidato autoral integrado | ROM + captura Sound Test + WAV |

Fonte autoral: `data/source_audio/forge_crystal_score.json`. O arranjo vigente é
compilado por `data/source_audio/build_forge_crystal_v2.py` e usa as quatro
vozes do SN76489: lead, baixo, contraponto/arpejo cristalino e ruído percussivo
curto. Não há sample comprimido na BGM; o PCM continua livre para golpes e KO.

Pipeline reprodutivel:

```text
build_forge_crystal_v2.py -> res/music/mus_forge_brand.vgm -> XGM/rescomp -> ROM
```

## 3. SFX

| SFX | Evento | Prioridade | Canal/driver | Risco de mascaramento | Evidencia |
|---|---|---|---|---|---|
| brand_hammer_slam | F120 contacto | 15 | XGM2 PCM CH2 + PSG noise/thump | BGM FM deve ceder o grave | sintetizado 13.3 kHz, placeholder |
| brand_stamp_whoosh | wordmark | 11 | PCM CH2 | nao compete com o slam | existente |

## 4. Integracao

- Driver: `Z80_DRIVER_XGM`; `XGM_startPlay(mus_forge_brand)` no inicio da luta.
- Politica de canais: PSG 0 lead, PSG 1 baixo, PSG 2 contraponto, PSG 3
  percussao; PCM CH3/CH4
  continua reservado aos SFX existentes de P1/P2.
- Regras de ducking: nao ha ducking falso; os SFX PCM tem prioridade sobre a
  cama tonal por nao compartilharem canal. O baixo foi transposto para a faixa
  segura do PSG para evitar aliasing e perda de corpo.
- Eventos reativos a beat: nenhum evento de gameplay depende do beat; a faixa
  e musical, nao uma fonte de temporizacao.
- Sound Test: OPTIONS -> SOUND TEST; A alterna play/stop, B retorna, e a faixa
  usa a mesma instancia de recurso da luta. `XGM_setLoopNumber(-1)` garante
  reproducao continua.
- Fallbacks: se a musica estiver OFF, a luta permanece silenciosa sem afetar
  SFX; Sound Test continua podendo auditionar explicitamente a faixa.

## 5. QA de Audio

- Score: `build_forge_crystal_v2.py` compila 768 frames NTSC, 8 compassos e
  loop deterministico; `rescomp` gera o recurso XGM sem PCM na BGM.
- Sem clique em loop: entrada de loop coincide com o frame 0 e todos os ataques
  sao desligados antes da proxima nota; confirmar por escuta em duas passagens.
- SFX criticos audiveis: permanecem em PCM CH3/CH4 e foram preservados no
  mesmo build.
- Audio em BlastEm: capturar `tests/capture_sound_test.py` e rodar
  `tests/audit_captured_audio_signal.py --wav ...`; este relatorio comprova
  sinal e rota, mas nao substitui escuta humana.
- Status atual: `buildado_emulator_signal_verified`; a captura same-ROM existe
  para Sound Test e luta, mas audição humana de timbre, loop, balanço e
  mascaramento continua obrigatória antes de `final`.

## 6. Evidência vigente — 21 de setembro de 2026

- ROM vigente: `b6f7cd649f829c21555883014721992b04261f0c32b34a620538d0548be7cc88`.
- Sound Test real: `out/emulator_evidence/sound_test_20260921T005842Z/`; a tela
  mostra `SOUND TEST / FORGE CRYSTAL`, e a rota PLAY/loop/STOP foi exercitada.
- WAV isolado: 48 kHz estéreo, 17,05 s, sinal presente, pico 3865, RMS -25,65
  dBFS, zero clipping e sink exclusivo do BlastEm.
- Combate com música: `out/emulator_evidence/visual_ko_20260921T005523892270Z-727484/`;
  vídeo/áudio de 87,6 s, 2 KOs, 42 hits e zero clipping. O agarrão, defesa e
  especial também foram exercitados em sessões same-ROM isoladas.
- Limite aberto: o relatório objetivo prova sinal/rota, não aprovação auditiva;
  a escuta humana e a avaliação do mix com SFX continuam pendentes.

## 7. Evidência current-SHA — 21 de setembro de 2026

- ROM: `d9334271d4e4dd6da33c9725d4734b994b4918dadff4510c981a54e6e133f58a`.
- Sound Test: `out/emulator_evidence/sound_test_20260921T021855Z/`, com
  TITLE -> OPTIONS -> SOUND TEST -> PLAY -> loop -> STOP observado no BlastEm.
- WAV isolado: 48 kHz estéreo, 18,15 s, pico PCM 3865, RMS -25,68 dBFS,
  zero clipping, rota do stream isolada validada.
- Estado: `signal_and_route_present`; isso não substitui escuta humana nem
  aprovação de timbre, emenda, balanço e mascaramento com SFX.
