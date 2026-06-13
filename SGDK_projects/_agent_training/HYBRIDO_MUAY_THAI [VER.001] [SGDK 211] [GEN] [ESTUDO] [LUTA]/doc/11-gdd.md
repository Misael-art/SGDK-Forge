# GDD - HYBRIDO MUAY THAI

Status: `training_lab_visual_rejected_v002`

## Escopo

Este projeto e um treino de criacao de lutador para Mega Drive. O objetivo de v002
e provar um viewer honesto com tres acoes legiveis, sem promover o placeholder v001
como arte final.

Revisao humana de 2026-06-07 reprovou a progressao visual v002. O viewer continua
util como prova tecnica de runtime, mas nao como personagem final ou candidato
premium.

## Personagem

- Lutador hibrido de Muay Thai com mutacao de pedra/lava.
- Silhueta: ombros largos, antebracos pesados, postura baixa e guarda fechada.
- Materiais: pedra, pele, bandagem, shorts e FX de fogo/glow separados.
- Acoes minimas: `idle`, `walk_step`, `teep`.
- Anatomia obrigatoria por pose: exatamente 2 bracos, 2 pernas, 1 cabeca e 1 tronco.
- Acting obrigatorio: idle focado; golpes com mandibula tensionada, dentes ou kiai; olhos sempre mirando o oponente.

## Qualidade visual

O projeto mira leitura comercial 16-bit, mas permanece `lab_not_delivery=true` ate
haver aprovacao humana, motion preview aprovado e evidencia BlastEm fresca.

v002 falhou este gate: Pose 3 le como tres bracos, o rosto nao muda em poses de
esforco e a traducao 48x64 perdeu olhos, lava, calcao e contraste material.

PNG tecnicamente valido, build limpo e ROM no BlastEm nao equivalem a aprovacao
artistica.

## Proibicao

`data/builders/build_hibrido_assets_v001.py` e `technical_lab_asset` e nao pode ser
tratado como fonte visual final.

`data/builders/build_hibrido_fighter_assets_v002.py` tambem e rota reprovada:
so pode ser usado com flag explicita de reproducao de laboratorio rejeitado.
