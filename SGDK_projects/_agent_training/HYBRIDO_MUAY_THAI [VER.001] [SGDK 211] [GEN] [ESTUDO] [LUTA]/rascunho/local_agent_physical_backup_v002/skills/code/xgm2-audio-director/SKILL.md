---
name: xgm2-audio-director
description: Use quando a tarefa envolver arquitetura de audio no Mega Drive com XGM2, ownership de canal PCM, BGM + SFX + ambiente simultaneos, pause/resume, loop e integracao de eventos de gameplay. Nao use para apenas tocar uma musica isolada, editar samples fora do pipeline ou discutir audio generico sem SGDK.
---

# XGM2 Audio Director

Esta skill existe para o gap puro de audio senior no workspace.

## Nao substitui outras skills

- `sgdk-runtime-coder`
  - continua dono da integracao C e do loop principal
- `sgdk-build-wrapper-operator`
  - continua dono do wrapper e do build
- `z80-pcm-custom-driver`
  - dono de drivers Z80 customizados, streaming PCM avancado, manipulacao direta de DAC/YM2612, PSG por registrador e qualquer tecnica alem do wrapper XGM2; esta skill coordena mas nao implementa low-level

## Ler antes de agir

1. `doc/05_technical/93_16bit_hardware_mastery_registry.json`
2. `sdk/sgdk-2.11/inc/xgm2.h`
3. samples oficiais relevantes em `sdk/sgdk-2.11/sample/`
4. `tools/sgdk_wrapper/.agent/skills/code/sgdk-runtime-coder/references/sgdk_211_api_reality.json`
5. `references/audio_event_contract.json`
6. `references/channel_ownership_templates.json`
7. `doc/05_technical/99_aaa_audio_architecture_guide.md`
8. `tools/sgdk_wrapper/validate_audio.ps1`
9. `tools/sgdk_wrapper/schemas/audio_architecture_card.schema.json`
10. `tools/sgdk_wrapper/schemas/composition_scope_contract.schema.json`
11. `tools/sgdk_wrapper/.agent/references/agentic_aaa_contracts/examples/audio_architecture_card.example.json`

## Quando usar

- definir ownership de canal
- tocar BGM, SFX, voz e ambiente sem corte indevido
- desenhar `typewriter_voice_text` sem roubar SFX critico
- implementar `pause`, `resume`, `stop` e loop limpo
- desenhar `audio_director.c` ou equivalente
- validar integracao de gameplay com eventos de audio

## Saidas obrigatorias

- `audio_architecture_card`
- `composition_scope_contract`
- `channel_ownership_map`
- `audio_channel_ownership_report`
- `dac_stream_budget_report` quando DAC/PCM for usado
- `sfx_priority_matrix`
- `audio_event_matrix`
- `sample_format_audit`
- `typewriter_voice_plan` quando texto tiver som por caractere, silaba ou speaker
- `loop_integrity_plan`
- `seamless_loop_report` quando houver BGM, ambience loop, menu loop ou faixa de fase
- `frequency_masking_plan` quando BGM coexistir com SFX, voz, passos, impacto, alerta ou UI
- `music_stem_export_plan` quando houver trilha modular, intensidade dinamica ou adaptive music
- `blastem_audio_proof_plan`
- `delivery_findings`

## Regras canonicas

- XGM2 e o padrao desta trilha
- toda composicao deve declarar `composition_scope_contract`: `micro_sketch_1m`, `core_loop_10m`, `modular_track_1h` ou `silence_intentional`
- `micro_sketch_1m` e permitido para laboratorio, placeholder, loading, menu simples, game jam ou prototipo; nao pode fechar entrega AAA nem virar trilha final sem promocao documentada
- `core_loop_10m` exige loop de 8-16 compassos ou duracao equivalente, `seamless_loop_report` e repeticao sem clique, corte ou fadiga perceptiva no contexto de gameplay
- `modular_track_1h` exige estrutura A/B, intro, ponte, stinger ou variacao formal, `frequency_masking_plan`, stems/layers quando aplicavel e `adaptive_music_state_map` quando a gameplay mudar intensidade
- todo canal DEVEM ter dono declarado
- `pause` de gameplay DEVE refletir no estado do audio
- loop de musica NAO pode clicar nem reiniciar de forma abrupta
- SFX nao podem cortar BGM por erro de ownership
- BGM nao pode mascarar SFX critico; a composicao deve reservar espaco para hit, dano, alerta, passos, tiros, UI, voz e boss cue
- sample rate e formato DEVEM ser auditados antes da integracao
- se houver assets de audio declarados em `.res`, `validate_audio.ps1` DEVE gerar `out/logs/audio_validation_report.json` antes do fechamento
- audio AAA nao e pos-processo: deve nascer no spec da cena quando houver stinger, ambience, boss cue, fade ou prioridade de SFX
- a direcao sonora e a tecnica de audio escolhida devem nascer no GDD/TDD com funcao de gameplay/narrativa, ownership, budget e fallback
- todo `audio_architecture_card` deve declarar `audio_role`, `xgm2_mode`, `channel_ownership_map`, `sfx_priority_table`, `music_stinger_plan`, `audio_transition_plan`, `pause_resume_contract` e `fallback_plan`
- todo `typewriter_voice_text` deve declarar cadence, prioridade, variacao por speaker e silencio dramatico; sem isso, usar texto sem SFX

## Senior Competencies

- `channel ownership`
  - BGM, SFX, voz e ambiente com responsabilidade explicita
- `composition scope management`
  - diferencia rascunho emergencial, loop funcional e faixa modular profissional antes de produzir ou integrar audio
- `event-driven audio`
  - gameplay despacha eventos; audio decide o canal correto
- `pause/resume integrity`
  - jogo e audio mantem coerencia de estado
- `loop-safe playback`
  - loops sem clique, sem corte e sem regressao silenciosa
- `modular adaptive scoring`
  - arranjo A/B, stems/layers, stingers e transicoes com funcao de gameplay
- `typewriter voice`
  - texto com som curto, ritmico e cancelavel, subordinado a alerta, dano, boss cue e pause

## Anti-padroes

- tocar tudo no mesmo canal por conveniencia
- chamar uma tecnica de audio de pronta sem prova simultanea
- vender `micro_sketch_1m` ou loop de prototipo como faixa final AAA
- aceitar loop com clique ou corte perceptivel
- declarar loop perfeito sem `seamless_loop_report`
- integrar sample sem auditar formato
- deixar BGM ocupar faixa, prioridade ou canal que esconda feedback critico
- deixar tick de texto mascarar SFX critico ou repetir sem pausa ate virar ruido
- misturar BGM linear com stinger sem declarar transicao
- deixar boss cue ou ambience entrar em rota de colisao com SFX de gameplay
- declarar faixa modular/adaptativa sem stems, layers, ownership e `adaptive_music_state_map`

## Anexo: `adaptive_music_state_map`

Quando o score precisa reagir a estado de gameplay (calm/pressure, fase do chefe, low health, sprint, hazard, victory, defeat), esta skill emite tambem um `adaptive_music_state_map` validado contra `tools/sgdk_wrapper/schemas/adaptive_music_state_map.schema.json`.

O `adaptive_music_state_map` declara:

- `trigger_sources` (eventos de gameplay que mudam o estado: health_threshold, phase_change, time_pressure, hazard, room_enter, boss_phase, victory, defeat)
- `music_states` (cada estado: id, role, intensity, base_track_id, layers, transition_type, transition_frames, fallback_track_id, bpm_hint, priority)
- `transition_graph` (lista de transicoes validas com from_state, to_state, trigger_source, fade_strategy, ducking_strategy)
- `channel_ownership_reservation` (garante que stinger/ambience nao colida com BGM/voice)
- `evidence_required` (BlastEm com sram dump, screenshot do estado, validate_audio sem regressao)

Regras:

- toda transicao precisa de `fade_strategy` (cut/crossfade/layer_fade/duck) e `transition_frames` (>=1)
- todo estado precisa de `fallback_track_id` quando nao houver layer redundante
- `priority` do estado nao pode colidir com SFX criticos de gameplay
- `bpm_hint` deve ser compativel com o ritmo declarado em `moodboard_manifest.palette_sharing_rules` (herdado do `art-direction-selector`)
- O mapa deve nascer ANTES de `sgdk-runtime-coder` integrar audio no loop, para que o runtime nao tenha que descobrir ownership a posteriori

## Integracao

- combinar com `sgdk-runtime-coder` para callbacks, update loop e runtime state
- combinar com `sgdk-build-wrapper-operator` e `workflows/build-validate.md` para gate de emulador e validacao real
- combinar com `z80-pcm-custom-driver` quando audio AAA exigir drivers customizados, streaming PCM avancado, manipulacao de DAC ou efeitos alem do XGM2; esta skill define a arquitetura e ownership, z80-pcm-custom-driver implementa o low-level
- combinar com `megadrive-vdp-budget-analyst` para coordenar DMA budget vs. bus contention com Z80 audio

## Contrato Operacional

### Entrada minima

- cena, estado ou feature com papel de audio declarado
- lista de BGM, SFX, voz, ambiente ou silencio intencional
- eventos de gameplay que disparam audio
- `.res` e assets de audio quando ja existirem

### Saida minima

- `audio_architecture_card`
- `composition_scope_contract`
- `channel_ownership_map`
- `audio_channel_ownership_report`
- `dac_stream_budget_report` quando houver PCM/DAC
- `sfx_priority_matrix`
- `audio_event_matrix`
- `sample_format_audit`
- `loop_integrity_plan`
- `seamless_loop_report` quando houver BGM ou ambience loop
- `frequency_masking_plan` quando musica e SFX coexistirem
- `music_stem_export_plan` quando a faixa for modular/adaptativa
- `blastem_audio_proof_plan`
- `delivery_findings`

### Passa quando

- `composition_scope_contract` declara profundidade, uso permitido, status ceiling e criterio de promocao
- `composition_scope_contract` valida contra `composition_scope_contract.schema.json` quando estiver em JSON
- todo canal tem dono e prioridade declarados
- `audio_architecture_card` valida contra `audio_architecture_card.schema.json` quando estiver em JSON
- `sfx_priority_matrix` protege SFX de gameplay contra tick de texto, ambience ou stinger secundario
- pause/resume, stop, fade e loop possuem contrato de runtime
- loops de musica e ambience possuem `seamless_loop_report` sem clique, silencio morto ou reinicio perceptivel
- BGM e mix musical passam pelo `frequency_masking_plan` para nao cobrir SFX critico
- trilha modular/adaptativa possui stems/layers, transicoes e fallback antes da integracao
- samples foram auditados por formato antes da integracao
- `validate_audio.ps1` e planejado ou executado quando houver audio em `.res`
- audio nao mascara feedback critico de gameplay
- toda tecnica de audio aplicada consta no registry/manifesto; driver Z80 customizado, DAC direto, PSG PCM ou CSM continuam restritos ao status humano vigente

### Handoff para proxima etapa

- entregar cards e matriz de eventos para `sgdk-runtime-coder`
- entregar assets e `.res` para `sgdk-build-wrapper-operator`
- acionar `z80-pcm-custom-driver` apenas quando XGM2 padrao nao cobre a necessidade
