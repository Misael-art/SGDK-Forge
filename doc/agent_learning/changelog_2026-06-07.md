# Changelog de Curadoria Canonica - 2026-06-07

Escopo avaliado:

- `SGDK_projects/_agent_laboratory`
- `SGDK_projects/_agent_training`
- `SGDK_projects/Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]`
- `SGDK_projects/SMOKE_TEST [VER.001] [SGDK 211] [GEN] [LAB]`

## Decisao

Curadoria aplicada com escopo conservador. Nenhuma tecnica foi promovida para
`MESTRE_*`, nenhuma skill nova foi criada e nenhum projeto/laboratorio foi
promovido como entrega. Foram aceitas apenas regras de baixo risco, com dono
canonico existente e base tecnica direta nos headers/scripts SGDK locais ou em
falhas reproduzidas nos ledgers.

## Canonizado

Arquivos alterados:

- `tools/sgdk_wrapper/.agent/skills/hardware/megadrive-vdp-budget-analyst/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/code/sgdk-runtime-coder/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/art/multi-plane-composition/SKILL.md`

Regras assimiladas:

- `SPR_getUsedVDPSprite()` nao e pressao por scanline; scanline claim exige
  `vdp_scanline_simulator.py`, dump/telemetria equivalente ou auditoria de pior
  quadro com posicoes reais.
- Bandas horizontais de parallax usam `HSCROLL_LINE` ou `HSCROLL_TILE`;
  `VSCROLL_COLUMN` nao expressa velocidades horizontais por faixa.
- Road stack, line scroll e deformacao por scanline nao devem gastar
  multiplicacao/divisao dentro de loop de 224 linhas por frame quando tabela,
  diferenca finita ou acumulador fix16/fix32 resolvem o mesmo efeito.
- Composicao com scroll precisa medir `populated_extent` e
  `signed_scroll_gutter`; aumentar o plano VDP nao cria continuidade se a arte
  autorada nao cobre o maior deslocamento real.

Tambem foi removido lixo gerado de `tools/sgdk_wrapper/modelo/out/` porque o
gate canonico exige que o template nao carregue artefatos de execucao.

## Nao Canonizado

Mantidos fora do canone por evidencia insuficiente, falta de fixture cruzada ou
risco de schema/validator sem regressao especifica:

- MUGEN SFF/DEF parser/export como skill ou ferramenta canonica.
- `mugen_stage_logical_composition_gate` como skill nova.
- `png_plte_trim_to_16` como skill nova.
- `preflight_host_files_count_array_wrap` como skill nova.
- novas propriedades obrigatorias em `road_physics_contract.schema.json` para
  Z visual/collision/parallax; o aprendizado fica registrado, mas schema nao
  foi endurecido sem fixtures.
- alteracao nova em `blastem_automation.psm1` para captura preta: o bloqueio
  de PrintWindow quase branco/preto ja estava implementado, entao nao houve
  patch duplicado.
- regras de model sheet do HYBRIDO como skill nova: anatomia, acting facial,
  scale/turnaround/marker continuity, material lock e separacao
  technical_pass/visual_pass ja estao cobertos por
  `visual-excellence-standards` e `art-translation-to-vdp`.

## Validacao

- `python tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py`:
  passed.
- `python tools/sgdk_wrapper/ci/test_schema_contract_gates.py`: `64/64`.
- `python tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py
  --self-check`: passed.
- `powershell -NoProfile -ExecutionPolicy Bypass -File
  tools/sgdk_wrapper/ci/run_all_contract_gates.ps1 -Mode full`:
  `combined_status=passed`.

Regra factual: esta curadoria melhora a disciplina do agente canonico em budget
VDP, scroll, pseudo-3D/road stack e composicao de planos. Ela nao valida ROM,
asset ou cena especifica; os projetos avaliados mantem seus bloqueios locais
conforme seus reports.
