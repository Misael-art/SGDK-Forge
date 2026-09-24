# Canonical Promotion Review

Use este arquivo para revisar, com cautela, se algum aprendizado local deve ser levado para o framework canonico.

## Politica

Promocao canonica so ocorre quando um humano ordenar explicitamente a assimilacao. Ate la, tudo permanece local e passivo.

## Checklist de revisao

| Item | Status |
|---|---|
| O aprendizado tem evidencia rastreavel? | [atendido: bundle, gate e ROM com o mesmo SHA-256] |
| O padrao funcionou fora de um caso unico? | [atendido: regressao sintetica 10/10 e fixture real no BlastEm] |
| Os riscos e limites estao escritos? | [atendido: `technical_fixture_contracts`, `ready_for_aaa=false`] |
| Existe conflito com `SGDK_GLOBAL.md`? | [nao identificado] |
| Existe conflito com headers SGDK 2.11? | [nao identificado; build SGDK 2.11 concluido] |
| Um humano aprovou a promocao? | [sim: ordem explicita do usuario] |

## Decisoes

| Data | Candidato | Decisao | Justificativa | Autor humano |
|---|---|---|---|---|
| [DATA] | [candidato] | `needs_human_review` | [motivo] | [nome/handle] |
| 2026-08-05 | sete contratos de fixture neutra | `implemented` | Promocao ordenada explicitamente pelo usuario; regressao host, ROM SGDK e bundle BlastEm vinculados ao mesmo hash | usuario do workspace |

## Fechamento

A promocao foi manual e explicitamente autorizada. O campo
`canonical_promotion_performed=false` produzido pelo extrator local permanece
correto: ele afirma que a automacao nao autoeditou o framework; nao desfaz a
curadoria humana registrada nesta decisao.
