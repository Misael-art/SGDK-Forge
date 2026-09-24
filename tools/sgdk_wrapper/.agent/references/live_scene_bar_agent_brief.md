# Brief — barra viva (leia antes de tocar arte ou runtime)

Doutrina: `doc/03_art/18_live_scene_bar.md`
Tetos: `doc/03_art/live_scene_bar_parameters.json`
Laudo: `out/logs/live_scene_bar_report.json`

Handles = oficio, nunca IP. Sem laudo o claim nao existe.

## Tetos (nao redesenhar)

| Recurso | Numero | Nao e |
|---|---|---|
| Tela de gate | H40 320×224 4:3 | widescreen / Mode 7 de vitrine |
| CRAM | 4 paletas × 16 | 4–8 paletas simultaneas |
| Palco denso | ~980 tiles BG+FG (observado) | dump de arcade; limite de silicio |
| SAT / linha H40 | 80 / 20 sprites, 320 px | 1000+ como default de produto |
| 2D arcade | 60 fps ou recuo no GDD | probe mudo |
| 3D software | FPS medido **com musica** | 60 fps de slogan |
| Plataforma critica | 0 lag frames | lag "de feel" |
| Som | YM2612 traduz identidade; driver medido na cena pesada | dump PCM; "XGM2 sempre mais leve" |
| SGDK | base, nao teto | desculpa para nao medir |

CPU/DMA % se **declara**. 90–97% e demo extrema, nao meta.

## Por modo

| Modo | Fazer | Nao fazer |
|---|---|---|
| criar | tetos no GDD/spec **antes** da arte | sprite primeiro |
| analisar | comparar numeros medidos com o JSON | promover no olho |
| treinar | ensinar tetos binarios | decorar handle |
| laboratorio | multiplex extremo, 3D, raycast, doubler so aqui (`lab_not_delivery`) | entregar lab como AAA |
| curadoria | promover numero/axioma so com prova em ROM | ensaio sem medicao |

## Sequencia

limites → planta em pixel → coreografia → medicao → orcamento → contrato
→ fonte forte → traducao nativa → segundo passe → ROM → evidencia

Proibido: pixel-art-sheet no gerador; dump de palco; PCM Neo/SNES como BGM;
uma paleta privada por skin; 60 fps sem cena+audio.
