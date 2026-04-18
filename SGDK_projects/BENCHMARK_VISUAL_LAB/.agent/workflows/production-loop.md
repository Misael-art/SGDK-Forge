# Workflow: Production Loop

Use este fluxo para o pipeline completo de uma iteracao: design -> arte -> runtime -> QA -> evidencia.

Cada passo referencia skills reais. A ordem canonica da jornada de cena AAA vive em:

- `workflows/aaa-scene-pipeline.md`
- `pipelines/aaa_scene_v1.json`

Nenhum passo pode ser pulado.

---

## Pipeline: Design -> Art -> Code -> QA -> Iteracao

### 1. Escopo e mecanica

Papel humano: direcao de produto.

- consultar `doc/11-gdd.md` e `doc/13-spec-cenas.md`
- delimitar escopo da iteracao
- registrar criterio de aceitacao

Saida minima:

- briefing aceito

### 2. Arte e composicao

Skills oficiais:

1. `art/art-asset-diagnostic`
2. `art/multi-plane-composition`
3. `art/art-translation-to-vdp`
4. `art/visual-excellence-standards`
5. `hardware/megadrive-vdp-budget-analyst`

Saida minima:

- laudos e artefatos de arte completos
- decisao explicita `cabe`, `cabe com recuo` ou `nao cabe`
- quando houver mais de uma rota visual honesta, `route_exploration_board` + `route_decision_record` antes do runtime

Regra de curadoria AAA:

- explorar alternativas e permitido
- reabrir a direcao visual do zero a cada iteracao, nao e permitido
- a exploracao deve acontecer dentro do mesmo `shared_canvas_contract` e congelar uma `locked_visual_direction` escolhida pelo usuario ou recomendada pelo juiz estetico

### 3. Integracao runtime

Skills oficiais:

- `code/sgdk-runtime-coder`
- `architecture/scene-state-architect`
- `operation/sgdk-build-wrapper-operator`

Saida minima:

- build limpo
- `runtime_decision_log`
- ROM gerada

### 4. Validacao e evidencia

Ferramentas e gates:

- `validate_resources.ps1`
- `workflows/build-validate.md`
- BlastEm obrigatorio
- `doc/changelog`
- `doc/10-memory-bank.md`

Saida minima:

- `validation_report.json`
- `emulator_session.json`
- changelog atualizado
- memoria operacional coerente

### 5. Iteracao

- triagem humana
- voltar para a skill da etapa afetada
- nunca corrigir no escuro sem registrar a classe real do erro

---

## Regras do Loop

- nenhum passo pode ser pulado
- assets nao validados nao entram no build
- budget nao e declarado por intuicao
- ROM nao testada nao e entregue
- changelog nao e opcional
- memoria operacional nao substitui evidência
- BlastEm fecha gate de entrega
