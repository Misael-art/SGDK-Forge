# Agent Learning - LIVE_BAR_FR2

Status: `active_local_closed_loop`

Este diretorio guarda aprendizado local deste projeto. O agente pode atualizar automaticamente `learning_ledger.json` e gerar propostas, mas nunca altera o framework canonico sem aprovacao humana explicita.

## Regra central

Nada neste diretorio promove automaticamente regras, skills, `lib_case`, registry ou workflows da `.agent` canonica.

Promocao canonica exige ato humano deliberado, revisao explicita e edicao controlada na fonte canonica apropriada.

## Como usar

Ao abrir o projeto:

1. leia este `README.md`;
2. se a tarefa for a abertura / marca / branding v2, leia primeiro
   `the_forge_opening_lessons.md` (caderno medido 2026-08-18);
3. consulte `success_patterns.md` e `failure_patterns.md`;
4. verifique `skill_promotion_candidates.md`;
5. respeite pendencias em `canonical_promotion_review.md`;
6. execute `audit_project_learning.ps1 -Mode Audit` e leia primeiro o `candidate_index`.

Ao encerrar uma tarefa relevante:

1. registre padroes comprovados por evidencia;
2. registre falhas, causas e mitigacoes;
3. classifique candidatos de promocao com conservadorismo;
4. execute `audit_project_learning.ps1 -Mode Capture`;
5. confirme `canonical_promotion_performed=false`.

## Classificacoes permitidas

| Classificacao | Uso |
|---|---|
| `local_note` | Observacao util apenas para este projeto. |
| `promotion_candidate` | Padrao possivelmente reutilizavel, ainda sem promocao canonica. |
| `do_not_promote` | Achado especifico, fragil, temporario ou arriscado. |
| `needs_human_review` | Requer decisao humana antes de qualquer uso canonico. |

## Ledger estruturado

`learning_ledger.json` consolida lições, grau de evidência, freshness, deduplicação, owner sugerido e propostas canônicas não aplicadas.

- o ledger pode ser atualizado automaticamente;
- propostas nascem `not_applied`;
- caminho externo ou evidência stale não sustenta promoção;
- skill nova só pode ser proposta quando não houver owner canônico existente;
- nenhum status `MESTRE_*` nasce deste ciclo.

## Relação com out/agent_learning

`doc/agent_learning/` e versionavel e serve como memoria local humana/agente.

`out/agent_learning/` e artefato runtime gerado por validacoes, gates ou experimentos. Ele nao deve ser versionado e nao substitui este diretorio.

O resumo operacional do ciclo fechado vive em `out/logs/project_learning_report.json`.
