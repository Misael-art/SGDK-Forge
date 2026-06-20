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
- `sound_chip_identity_plan` dentro do `audio_architecture_card` quando houver musica final, referencia sonora, identidade de genero, FM/PSG/DAC ou PCM
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
- quando a cena tiver identidade musical/sonora, referencia externa, PCM ou faixa final, o `audio_architecture_card` tambem deve declarar `sound_chip_identity_plan`
- Mega Drive nao deve ser tratado como SNES com menos memoria: referencias orquestrais/sampleadas precisam ser traduzidas para papeis FM, PSG e DAC curtos, sem assumir eco/reverb nativo ou RAM de samples dedicada
- FM do YM2612 e direcao de timbre: baixo, lead, pad, arp, percussao e stinger precisam ter papel, canal dono e objetivo perceptivo antes de virar faixa final
- DAC/PCM sacrifica ownership convencional do canal e exige budget/validacao; voz ou bateria sampleada nao entra como "gratis" na mix
- PSG deve ter papel util: UI, noise, acentos, drones ou fallback; se ficar sem papel, nao ocupar canal por habito
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
- `YM2612 FM timbre design`
  - traduz fantasia musical em patch palette: baixos, leads, pads, arps, stingers e percussao FM com dono de canal e funcao de gameplay
- `platform sound translation`
  - converte referencias SNES/orquestrais/sampleadas em decisao Mega Drive coerente, sem prometer eco nativo, sample RAM dedicada ou reverb sem custo

## Anti-padroes

- tocar tudo no mesmo canal por conveniencia
- tentar soar como SNES por acumulacao de samples/eco, ignorando que o Mega Drive depende de FM/PSG/DAC e budget de barramento
- usar sample orchestral longo como identidade principal sem ROM budget, sample audit e fallback FM/PSG
- dizer "FM synth" sem declarar patch palette, canal dono e papel perceptivo
- usar DAC/PCM sem reconhecer tradeoff com FM_CH6/ownership XGM2
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

## Curadoria candidata: composicao adaptativa e clock musical

Origem: transcricao anexada em 2026-06-17 sobre criacao de musica para jogos,
evidencia `E1_text`. Esta expansao e candidata, reusa contratos existentes e nao
promove audio, ROM, runtime ou qualidade final sem prova auditiva/emulador.

### Regras aceitas com traducao para Mega Drive

- `vertical remixing` so e aceito como arranjo pre-planejado de estados, stems,
  layers ou variantes exportadas. Nao assumir automacao livre de middleware
  moderno.
- `horizontal resequencing` vira `bar_beat_transition_plan`: BPM, assinatura de
  compasso, frames por beat/bar em NTSC/PAL, pontos de troca permitidos,
  stinger/bridge ids e fallback quando a janela musical for perdida.
- Toda mudanca de estado musical precisa ser despachada por evento de gameplay;
  o gameplay pede uma intencao, o audio director agenda a troca no ponto musical
  permitido.
- Loop musical final exige `seamless_loop_report` com inicio/fim do loop, limite
  de compasso ou amostra, tratamento de clique, silencio morto e cauda sonora.
- Cauda de reverb/tail wrapping e tecnica de exportacao/edicao de asset; nao e
  reverb runtime gratuito no Mega Drive.
- `adaptive_music_state_map` deve declarar intensidade, prioridade,
  convivencia com SFX critico, ownership de canal e fallback audivel para cada
  estado.

### Rejeicoes explicitas desta fonte

- FMOD, Wwise, RTPC, filtros dinamicos e mixagem continua nao sao capacidades
  nativas assumidas no Mega Drive; quando a intencao for valida, traduza para
  estados discretos, fades suportados, stingers, variantes pre-renderizadas ou
  handoff para driver customizado.
- Exemplo C de video/transcricao nao vira API canonica: qualquer chamada XGM2,
  JOY, VDP ou debug UI deve ser confirmada nos headers SGDK 2.11 e pelas skills
  donas antes de entrar em projeto.
- Calculo de "tempo forte" nao pode usar numero magico: declare BPM,
  assinatura, regiao NTSC/PAL e se a troca ocorre em beat, meio compasso ou
  inicio de compasso.
- Interface de debug com texto, leitura direta de controle ou limpeza de plano
  em loop nao prova arquitetura de audio e nao deve ser copiada para producao.

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
- `sound_chip_identity_plan` quando houver musica final, identidade sonora ou referencia sonora a traduzir
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
- `sound_chip_identity_plan` declara escola sonora, papeis FM/PSG/DAC, politica para referencias SNES/sampleadas e suposicoes proibidas
- samples foram auditados por formato antes da integracao
- `validate_audio.ps1` e planejado ou executado quando houver audio em `.res`
- audio nao mascara feedback critico de gameplay
- toda tecnica de audio aplicada consta no registry/manifesto; driver Z80 customizado, DAC direto, PSG PCM ou CSM continuam restritos ao status humano vigente

### Handoff para proxima etapa

- entregar cards e matriz de eventos para `sgdk-runtime-coder`
- entregar assets e `.res` para `sgdk-build-wrapper-operator`
- acionar `z80-pcm-custom-driver` apenas quando XGM2 padrao nao cobre a necessidade
