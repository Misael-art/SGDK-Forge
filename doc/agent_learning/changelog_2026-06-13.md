# Agent Learning Changelog - 2026-06-13

## Art + Game Design Direction Gate

- Estudo: `SGDK_projects/_agent_training/HYBRIDO_MUAY_THAI [VER.001] [SGDK 211] [GEN] [ESTUDO] [LUTA]`.
- Sintoma: sprite sheet v009 tecnicamente valido, mas visualmente generico, sem preservar o model sheet v008 nem o contexto de luta/camera/interacao.
- Nova regra: asset critico visual exige `art_gameplay_direction_gate` antes de prompt, redraw, conversao ou promocao.
- Escopo do gate: model sheet, background, sprite art, key pose, animation strip, sprite sheet final, FX sheet, HUD heroico, title/menu ou asset critico.
- Marcadores obrigatorios: cabelo, olhos, rosto, roupa, emblemas, cicatrizes, caracteristicas fisicas unicas, armas, acessorios, materiais, assimetrias, landmarks e sinais de UI.
- Contratos canônicos: `tools/sgdk_wrapper/schemas/art_gameplay_direction_gate.schema.json` e `tools/sgdk_wrapper/ci/test_art_gameplay_direction_gate.ps1`.
- Status: v009 permanece rejeitado; nenhuma ROM ou asset foi promovido.
