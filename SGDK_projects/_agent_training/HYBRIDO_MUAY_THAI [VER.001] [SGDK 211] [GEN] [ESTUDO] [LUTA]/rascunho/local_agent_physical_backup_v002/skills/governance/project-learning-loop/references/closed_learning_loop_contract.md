# Closed Learning Loop Contract

## Fronteira

O ciclo automático termina na proposta local. Ele pode ler evidências, atualizar o ledger do projeto, deduplicar owners e sugerir testes. Ele não edita o cânone.

## Fluxo

`experiência -> lição local -> evidência -> deduplicação -> proposta -> revisão humana -> patch controlado -> regressão`

## Evidência

| Grau | Significado | Uso |
|---|---|---|
| `E0_note_only` | observação sem artefato | contexto local |
| `E1_artifact` | documento ou artefato local | investigação |
| `E2_build` | build/ROM vinculada | candidato operacional |
| `E3_blastem` | execução BlastEm vinculada | candidato testado |
| `E4_budget_and_regression` | budget e regressão vinculados | revisão canônica |
| `E5_cross_project_reproduction` | reproduzido em mais de um projeto | forte candidato reutilizável |

Evidência stale ou externa não sustenta promoção.

## Lifecycle

| Status | Significado |
|---|---|
| `observed` | achado recém-registrado |
| `evidence_incomplete` | faltam provas operacionais |
| `qualified_local` | útil e comprovado apenas localmente |
| `human_review_required` | existe proposta, mas nenhuma autorização |
| `approved_for_canonical_patch` | humano aprovou o escopo do patch |
| `implemented` | patch controlado existe |
| `verified` | regressão do patch passou |
| `rejected` | proposta recusada |
| `superseded` | substituída por entendimento posterior |

Somente ação humana pode definir `approved_for_canonical_patch`, `implemented`, `verified`, `rejected` ou `superseded`.

## Routing

Antes de sugerir skill nova:

1. procurar owner existente no catálogo;
2. preferir patch de regra, validator, schema, workflow, `lib_case`, doc ou skill dona;
3. criar proposta de skill somente para gap procedural puro e reutilizável;
4. manter falha desconhecida como `human_review`, nunca como prática recomendada.

## Segurança

- `Audit`: read-only.
- `Capture`: escreve somente `doc/agent_learning/learning_ledger.json` e `out/logs/project_learning_report.json`.
- `Capture` repetido sem mudanca semantica nas fontes deve ser byte-idempotente no ledger;
- toda proposta nasce `not_applied`;
- `canonical_promotion_performed` permanece `false` durante captura automática;
- promoção para `MESTRE_*` nunca é produzida por este ciclo.
