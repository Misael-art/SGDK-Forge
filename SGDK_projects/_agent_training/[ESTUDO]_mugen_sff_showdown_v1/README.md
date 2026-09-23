# [ESTUDO] MUGEN SFF v1.01 -> SGDK (Showdown)

Status: `controlled_training_area`

Objetivo: treinar o agente para ler `.sff` (SFF v1.01), reconstruir camadas/frames via `.def`, otimizar em tiles 8×8 (dedup + H/V flip + auditoria de sub-paletas) e gerar um viewer SGDK com evidência no BlastEm.

Entradas (fixture):
- `rascunho/inputs/` contém cópia local dos arquivos do stage.
- `rascunho/inputs_manifest.json` registra hashes e origem.

Saídas esperadas:
- `work/` extrações, reconstruções e artefatos intermediários.
- `analysis/` relatórios e evidências de otimização.
- `sgdk_viewer/` projeto SGDK mínimo para prova em emulador.
- `evidence/` screenshot BlastEm e dumps/relatórios finais.

Bloqueios:
- `lab_not_delivery=true`
- nunca declarar `ready_for_aaa=true`

