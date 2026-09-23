# 17 - Audio Design Document - MARE_BRAVA

## Direcao

O CAIS_01 usa YM2612/PSG/DAC como identidade: baixo FM quente, percussao curta e
ruido de agua subordinado ao impacto. A musica deve marcar entrada de onda e
respirar nas zonas de respiro; SFX de golpe, telegraph e ring-out sempre vencem a
mixagem.

## Escopo atual

- BGM de gameplay: `cais01_theme_pending`, escopo `core_loop_10m`, ainda sem fonte.
- SFX de branding: cinco WAV XGM2 declarados e validados em
  `out/logs/audio_validation_report.json` (5 amostras, 0.73% do orçamento ROM).
- SFX de gameplay: contratos de prioridade emitidos, assets e prova BlastEm ainda
  pendentes.
- Música adaptativa: estados e transições planejados em
  `doc/adaptive_music_state_map.json`; não promover até existir faixa e loop report.

## Ownership e QA

O contrato executável é `doc/audio_architecture_card.json`, com ownership de todos
os canais, limite de dois PCM simultâneos e fallback sem BGM. A promoção requer
`seamless_loop_report`, `frequency_masking_plan`, `validate_audio` e captura
BlastEm com o hash vigente. Estado atual: `needs_review`.
