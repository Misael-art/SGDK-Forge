# Canonical Promotion Review

Use este arquivo para revisar, com cautela, se algum aprendizado local deve ser levado para o framework canonico.

## Politica

Promocao canonica so ocorre quando um humano ordenar explicitamente a assimilacao. Ate la, tudo permanece local e passivo.

## Checklist de revisao

| Item | Status |
|---|---|
| O aprendizado tem evidencia rastreavel? | [pendente] |
| O padrao funcionou fora de um caso unico? | [pendente] |
| Os riscos e limites estao escritos? | [pendente] |
| Existe conflito com `SGDK_GLOBAL.md`? | [pendente] |
| Existe conflito com headers SGDK 2.11? | [pendente] |
| Um humano aprovou a promocao? | [pendente] |

## Decisoes

| Data | Candidato | Decisao | Justificativa | Autor humano |
|---|---|---|---|---|
| [DATA] | [candidato] | `needs_human_review` | [motivo] | [nome/handle] |
| 2026-07-29 | L11/L12 — roteamento de build SGDK por host e proveniencia LTO | `promoted_with_explicit_human_authorization` | Mismatch foi reproduzido no link direto e a rota Linux isolada gerou ROM; limites Linux/Windows e teto `buildado_emulator_pending` foram documentados, automatizados e cobertos por regressao | responsavel humano do workspace nesta sessao |

### Revisao especifica L11/L12

| Item | Status |
|---|---|
| Evidencia rastreavel | `passed`: route report, build report e hash da ROM |
| Generalizacao segura | `bounded`: regra de triagem e selecao; bridge apenas Linux |
| Riscos e limites | `passed`: sem transferencia de evidencia de emulador/AAA |
| Conflito com `SGDK_GLOBAL.md` | `none_found` |
| Conflito com headers SGDK 2.11 | `not_applicable`: nenhuma API runtime alterada |
| Aprovacao humana | `explicit_2026-07-29` |
| Aplicacao canonica | `completed`: selector, schema, preflight, enforcement em `build.bat`/bridge, skill, metadata e workflow |
| Regressao | `passed`: 5 cenarios do seletor + schema + skill validator |
