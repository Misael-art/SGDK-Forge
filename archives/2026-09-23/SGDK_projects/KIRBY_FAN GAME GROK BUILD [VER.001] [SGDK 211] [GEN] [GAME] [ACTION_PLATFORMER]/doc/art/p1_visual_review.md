# P1 — Revisao visual arquivada

Data: 2026-08-06
Escopo: 16 assets do `PRODUCTION_ASSET_PACK`; C5 explicitamente excluido.

## Veredito substitutivo

`archived_visual_rejected` em 2026-08-06, por julgamento explícito do
solicitante. A aprovação técnica abaixo é histórica e não vale como aprovação
artística. A pasta completa foi preservada em
`data/source_art/archive/p1_2026-08-06_visual_rejected/p1/`; P1 não é fonte
válida para gerar ou integrar arte nova.

## Resultado histórico

- 16/16 PNGs entregues originalmente em `data/source_art/p1/<id>/`.
- 16/16 passam dimensao, RGB333, chave, teto de cores, escada de valor, costura e vaos aplicaveis.
- Todos sao PNG indexado em grid nativo, sem interpolacao.
- Cada pasta possui `notes.md` e `prompt_used.txt`.
- A1 foi refeita do zero a partir do model sheet R2; a draft radial anterior foi preservada somente em `obsolete_technical_pass_visual_fail/` e nao participa da linhagem.
- A1 passa `sprite_artifact_report.v2`: 8 frames, zero clipping, ilhas, falha anatomica, drift, contato ausente ou delta invalido.

## Leitura visual por grupo

| Grupo | Veredito offline | Observacao |
|---|---|---|
| A | `passed_for_source_candidate` | A1 tem poses funcionais distintas; corrida ainda pede julgamento a 60 fps. |
| B | `passed_for_source_candidate` | Escada 0.512 -> 0.462 -> 0.324 -> 0.200 preserva profundidade e terreno comunica piso/vao. |
| C | `passed_for_source_candidate` | Face calmo/bravo le a 48x32; galho e tronco ainda dependem da montagem do boss. |
| D | `passed_for_source_candidate` | As cinco habilidades se distinguem pela forma, nao apenas cor. |
| E | `passed_for_source_candidate` | Logo autoral gordo/arredondado; composicao 320x224 ainda pendente. |

## Evidencia

- `data/source_art/p1/p1_asset_validation_report.json`
- `data/source_art/p1/p1_delivery_manifest.json`
- `data/source_art/p1/evidence/group_a_contact_sheet.png`
- `data/source_art/p1/evidence/group_b_contact_sheet.png`
- `data/source_art/p1/evidence/group_c_d_contact_sheet.png`
- `data/source_art/p1/evidence/group_e_contact_sheet.png`
- `data/source_art/p1/A1/sprite_artifact_report.json`
- `data/source_art/p1/A1/evidence/idle_vs_float_silhouette.png`
- `data/source_art/p1/A1/evidence/animated/run.gif`

## Limite histórico

O estado histórico era `source_candidate_complete`, mas está substituído por
`archived_visual_rejected`. Nenhum PNG P1 foi copiado para `res/`.
