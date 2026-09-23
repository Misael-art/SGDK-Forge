# Curadoria canonica — Celestial Chase Revive

Data: 2026-06-19

## Fonte

Projeto:
`SGDK_projects/Celestial Chase Revive [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_RACING]`

Evidencias principais declaradas pelo projeto:

- `doc/10-memory-bank.md`
- `doc/code_review_report.json`
- `doc/sprite_animation_audit_v020.json`
- `doc/scene_closeout_report.json`

## Decisao

Foram promovidas seis invariantes:

1. separar host, toolchain, runtime e qualidade criativa;
2. tratar metadados RESCOMP como autoridade para frames;
3. exigir input observado, nao apenas enviado;
4. ligar evidencia ao hash exato da ROM;
5. separar fechamento tecnico de promocao criativa;
6. corrigir por causa confirmada com regressao antes do patch.

Sete mecanismos permanecem em piloto:

- preflight machine-readable de capacidades do host;
- resultado transacional por estagio do wrapper;
- negociacao de transporte de input;
- linter de animacao contra metadados gerados;
- DAG formal de closeout;
- precedencia de evidencia VDP sobre heuristica;
- recuperacao estruturada da verdade de projeto legado.

Foram rejeitados:

- transporte de input especifico como regra universal;
- relaxamento de gate para produzir sucesso aparente.

## Integracao

- protocolo: `.agent/references/production_truth_protocol.md`
- workflow: `.agent/workflows/production-diagnostic-triage.md`
- registro: `.agent/references/celestial_chase_canonical_learning_review_2026-06-19.json`
- teste: `tools/sgdk_wrapper/ci/test_celestial_chase_canonical_learning.ps1`

## Estado

`validated_framework_no_rom`

Validacao executada em 2026-06-20:

- gate agregado de curadoria: passed;
- aprendizado local: 33/33;
- schemas: 73/73;
- ambiente/Graphify: 28/28.

Esta validacao cobre o framework. Nao constitui prova de ROM, emulador, budget
VDP ou qualidade AAA.
