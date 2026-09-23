# Agent Learning - SMOKE_TEST [VER.001] [SGDK 211] [GEN] [LAB]

Status: `passive_local_context`

Este diretorio guarda aprendizado local e consultivo deste projeto. Ele ajuda agentes futuros a entenderem decisoes, erros, padroes e candidatos de promocao sem alterar o framework canonico.

## Regra central

Nada neste diretorio promove automaticamente regras, skills, `lib_case`, registry ou workflows da `.agent` canonica.

Promocao canonica exige ato humano deliberado, revisao explicita e edicao controlada na fonte canonica apropriada.

## Como usar

Ao abrir o projeto:

1. leia este `README.md`;
2. consulte `success_patterns.md` e `failure_patterns.md`;
3. verifique `skill_promotion_candidates.md`;
4. respeite pendencias em `canonical_promotion_review.md`;
5. trate ausencia ou incompletude como contexto ausente, nao como blocker automatico.

Ao encerrar uma tarefa relevante:

1. registre padroes comprovados por evidencia;
2. registre falhas, causas e mitigacoes;
3. classifique candidatos de promocao com conservadorismo;
4. nao edite `.agent`, skills, `lib_case` ou registry com base apenas neste diretorio.

## Classificacoes permitidas

| Classificacao | Uso |
|---|---|
| `local_note` | Observacao util apenas para este projeto. |
| `promotion_candidate` | Padrao possivelmente reutilizavel, ainda sem promocao canonica. |
| `do_not_promote` | Achado especifico, fragil, temporario ou arriscado. |
| `needs_human_review` | Requer decisao humana antes de qualquer uso canonico. |

## Relação com out/agent_learning

`doc/agent_learning/` e versionavel e serve como memoria passiva humana/agente.

`out/agent_learning/` e artefato runtime gerado por validacoes, gates ou experimentos. Ele nao deve ser versionado e nao substitui este diretorio.
