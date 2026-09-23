# Spec de Cena - Viewer HYBRIDO MUAY THAI v002

Status: `implemented_lab_rejected_visual`

## Cena

- `scene_id`: `hibrido_fighter_viewer_v002`
- Papel: viewer ROM para alternar animacoes do lutador.
- Controles: esquerda/direita alternam `idle`, `walk_step` e `teep`.
- Papel atualizado: preservar prova tecnica de viewer, nao validar arte final.

## Recursos

- Corpo em PAL2: pedra, pele, bandagem e roupa.
- FX em PAL3: glow, fogo e impacto.
- Celula fixa: 48x64, pivo em 24,58.
- Runtime: dois sprites sobrepostos, body + FX.

## Budget

- Pior quadro local: body + FX do `teep`.
- Sem streaming por frame.
- Sem HUD final; texto/debug nao e identidade visual.
- A cena deve permanecer laboratorio ate captura BlastEm e revisao humana.
- A revisao humana atual rejeitou v002; proxima rota exige novo source/redraw com input gatekeeper anatomico e acting facial.

## Evidencia v002

- ROM sha256: `246b33725b479402cccf41cd28a1be79f6687c4524af0dbd74b4062021a978bc`.
- Screenshot BlastEm: `out/evidence/blastem/screenshot.png`.
- SRAM BlastEm: `out/evidence/blastem/save.sram`.
- `visual_vdp_dump.bin`: pendente.

## Bloqueios visuais

- `ANATOMY_EXTRA_LIMB_POSE_3`: source/model sheet le como tres bracos.
- `STATIC_FACE_ACTING`: idle, knee e teep/kick usam a mesma face fria.
- `RUNTIME_48X64_FIDELITY_FAILED`: olhos, lava, calcao e contraste quente nao sobrevivem no BlastEm.
- `TECHNICAL_PASS_DOES_NOT_IMPLY_VISUAL_PASS`: build/PNG/ROM nao aprovam arte.
