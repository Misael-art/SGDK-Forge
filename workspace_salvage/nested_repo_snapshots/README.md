# Nested Repo Snapshots

Este diretório preserva snapshots dos repositórios Git aninhados que não puderam
ser promovidos diretamente para o monorepo sem criar `gitlinks` ou submódulos
acidentais.

Objetivo desta passada:

- manter o conteúdo útil seguro no remoto
- evitar carregar o metadado `.git` interno para o monorepo
- registrar de forma explícita quais raízes foram salvas como snapshot

Snapshots gerados nesta wave:

- `platformerstudio_editor_snapshot.zip`
- `raycastingengine_3d_snapshot.zip`
- `mega_genius_puzzle_snapshot.zip`
- `msu_example_audio_snapshot.zip`
- `state_machine_rpg_snapshot.zip`

Raízes originais:

- `SGDK_Engines/PlatformerStudio [VER.1.0] [SGDK 211] [GEN] [ENGINE] [EDITOR]`
- `SGDK_Engines/RaycastingEngine [VER.1.0] [SGDK 211] [GEN] [ENGINE] [3D]`
- `SGDK_Engines/mega genius [VER.001] [SGDK 211] [GEN] [GAME] [PUZZLE]/mega genius`
- `SGDK_Engines/msu-example [VER.001] [SGDK 211] [GEN] [ENGINE] [AUDIO]/msu-example`
- `SGDK_Engines/state machine RPG [VER.001] [SGDK 211] [GEN] [ENGINE] [RPG]/state_machine`

Limites conhecidos:

- o histórico Git interno dessas raízes não entra neste snapshot
- o conteúdo foi salvo como evidência/backup operacional
- se essas raízes precisarem virar diretórios normais do monorepo no futuro,
  isso deve ser feito em uma passada própria de normalização
