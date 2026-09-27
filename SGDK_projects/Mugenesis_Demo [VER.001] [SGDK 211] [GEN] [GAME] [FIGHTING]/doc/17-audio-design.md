# 17 - Audio Design Document - Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]

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
| musica_de_luta | luta Suzaku | tensao e pulso durante combate, espaco para vozes/impactos | 8 compassos originais em D in-sen, 120 BPM | loop candidato 16s | staging_candidate; escuta e mix pendentes | `rascunho/processado/suzaku_fight_audio/suzaku_fight_loop_candidate_report.json` |

## 3. SFX

| SFX | Evento | Prioridade | Canal/driver | Risco de mascaramento | Evidencia |
|---|---|---|---|---|---|
| brand_hammer_slam | F120 contacto | 15 | XGM2 PCM CH2 + PSG noise/thump | BGM FM deve ceder o grave | sintetizado 13.3 kHz, placeholder |
| brand_stamp_whoosh | wordmark | 11 | PCM CH2 | nao compete com o slam | existente |

## 4. Integracao

- Driver: XGM2 existente. `AUDIO_playCue` dos cinco cues PSG simples deixou
  de chamar `AUDIO_stopAll`, que tambem desligava XGM2; build ROM
  `05a27a06...` passou, mas a continuidade sonora do menu nao foi ouvida.
- O build padrao inicia diretamente na luta (`MG_DIRECT_FIGHT=1` em
  `src/core/app.c`). O runner com `target_scene=2` capturou a luta, logo
  `audio.raw` desta sessao nao valida a musica de menu. Exigir build com
  perfil de menu explicito e comparacao antes/depois do cue.
- Um perfil isolado `-DMG_DIRECT_FIGHT=0` gerou ROM `1898bdc7...` e captura
  BlastEm com `scene_id=2`/menu e audio nao vazio. Ainda faltam evento de
  navegacao, comparacao da trilha antes/depois, escuta e loop; o conteudo do
  `audio.raw` nao foi aprovado apenas por existir.
- O builder autoral `data/source_art/branding_v2/build_forge_brand_vgm.py`
  escrevia os campos VGM de amostras/loop/rate deslocados em +4 bytes.
  O [contrato VGM v1.70](https://vgmrips.net/wiki/VGM_Specification) usa
  total @0x18, loop relativo @0x1C, amostras do loop @0x20, rate @0x24.
  Corrigido e testado: 423360/228/423360/60, alvo do loop `0x100`, dentro
  do arquivo de 1465 bytes. ROM isolada corrigida `f08d3fcd...` compilou.
  Capturas longas das ROMs anterior e corrigida (ambas `scene_id=2`, 1411
  frames) apresentaram sinal float32 nao nulo na maior parte da janela.
  Portanto **nao** atribuir ao cabecalho um silencio audivel ja provado:
  o conversor/driver/reinicio pode ter compensado. Falta escutar a juncao,
  testar cue simultaneo e validar loop/mix em evidencia sincronizada.
- Politica de canais:
- Regras de ducking:
- Eventos reativos a beat:
- Fallbacks:
  - Candidate loop no longer than 16s; if PSG noise masks impacts, test the same
    FM arrangement without PSG accents before revising the composition.

### Candidate de luta em staging — 2026-09-26

- O gerador `rascunho/processado/suzaku_fight_audio/build_suzaku_fight_vgm.py`
  cria uma composicao original de 8 compassos: ostinato grave, motivo FM
  pentatonico D/E/F/A/Bb, cama harmonica e resposta baixa esparsa. BPM=120;
  o VGM 1.70 tem 960 frames/705600 samples por loop NTSC (16s), fecha a contagem
  e deixa PCM XGM2 sem uso pela trilha para vozes/impactos.
- SHA VGM `a6edd4b104935d86e7cef35013d69075506454a51e770fa4732e938f2dc6ef09`;
  o ResComp 3.95 aceitou `XGM2 mus_suzaku_fight` com raw size 1024 bytes.
  Recibos: `suzaku_fight_loop_candidate_report.json` e
  `suzaku_fight_xgm2_rescomp_report.json` no mesmo diretorio.
- E um candidato composto por script. A cópia descartável de audição foi
  buildada e capturada no BlastEm, com início da faixa ao entrar na luta;
  a produção não foi alterada. O sinal passou os checks objetivos de duração,
  presença e clipping, mas ainda não houve audição humana, teste aprovado da
  costura, mix com vozes/impactos/super ou integração ao `res/resources.res`
  de produção. Não substituir `mus_forge_brand` nem aprovar a faixa antes
  desses gates.

### Captura isolada e sinal objetivo — 2026-09-26

- ROM descartável SHA-256 `fa7d859b666601ea3c0d2567031c15723a996d16237674c9c4b8076557427d72`;
  BlastEm observou `scene_id=3` e selou o bundle.
- O sidecar `audio.raw` tem 15,319,040 bytes, 48 kHz, estéreo float32. WAV
  derivado sem normalização: 39.893333 s, PCM s16le, pico -7.96 dBFS, RMS
  -22.60 dBFS, sinal presente e sem clipping digital. Canais duplicados (mono).
- Evidência e relatório: `rascunho/processado/suzaku_fight_audio/blastem_auditions/blastem-linux-20260926T090235Z-2327237/`; abrir
  `audio.wav` e `audio_audition_review.json`. Os resultados automáticos
  medem integridade do sinal, não qualidade ou aprovação musical.
- Título de janela: 59.7 fps em uma amostra. A sonda fixa de 1200 quadros
  marcou 74 quadros acima do orçamento e pico CPU 146. O causador não foi
  isolado; comparar build equivalente sem a BGM candidata. A janela capturada
  ainda usa o fundo placeholder e não prova performance com cenário.
- Permanecem pendentes: audição humana da identidade e emenda; mistura com
  vozes, impactos, PSG e super; validação de cadência sustentada e captura
  audiovisual com o cenário selecionado.

## 5. QA de Audio

- Sem clique em loop:
- SFX criticos audiveis:
- Audio OK em BlastEm:
- Evidencia:
