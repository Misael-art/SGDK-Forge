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

## Ler antes de agir

1. `doc/05_technical/93_16bit_hardware_mastery_registry.json`
2. `sdk/sgdk-2.11/inc/xgm2.h`
3. samples oficiais relevantes em `sdk/sgdk-2.11/sample/`
4. `tools/sgdk_wrapper/.agent/skills/code/sgdk-runtime-coder/references/sgdk_211_api_reality.json`

## Quando usar

- definir ownership de canal
- tocar BGM, SFX, voz e ambiente sem corte indevido
- implementar `pause`, `resume`, `stop` e loop limpo
- desenhar `audio_director.c` ou equivalente
- validar integracao de gameplay com eventos de audio

## Saidas obrigatorias

- `audio_architecture_card`
- `channel_ownership_map`
- `audio_event_matrix`
- `sample_format_audit`
- `loop_integrity_plan`
- `blastem_audio_proof_plan`
- `delivery_findings`

## Regras canonicas

- XGM2 e o padrao desta trilha
- todo canal DEVEM ter dono declarado
- `pause` de gameplay DEVE refletir no estado do audio
- loop de musica NAO pode clicar nem reiniciar de forma abrupta
- SFX nao podem cortar BGM por erro de ownership
- sample rate e formato DEVEM ser auditados antes da integracao
- audio AAA nao e pos-processo: deve nascer no spec da cena quando houver stinger, ambience, boss cue, fade ou prioridade de SFX
- todo `audio_architecture_card` deve declarar `audio_role`, `xgm2_mode`, `channel_ownership_map`, `sfx_priority_table`, `music_stinger_plan`, `audio_transition_plan`, `pause_resume_contract` e `fallback_plan`

## Senior Competencies

- `channel ownership`
  - BGM, SFX, voz e ambiente com responsabilidade explicita
- `event-driven audio`
  - gameplay despacha eventos; audio decide o canal correto
- `pause/resume integrity`
  - jogo e audio mantem coerencia de estado
- `loop-safe playback`
  - loops sem clique, sem corte e sem regressao silenciosa

## Anti-padroes

- tocar tudo no mesmo canal por conveniencia
- chamar uma tecnica de audio de pronta sem prova simultanea
- aceitar loop com clique ou corte perceptivel
- integrar sample sem auditar formato

## Integracao

- combinar com `sgdk-runtime-coder` para callbacks, update loop e runtime state
- combinar com `megadrive-elite` para gate de emulador e validacao real
