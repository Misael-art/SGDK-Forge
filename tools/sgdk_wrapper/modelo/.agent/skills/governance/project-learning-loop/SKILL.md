---
name: project-learning-loop
description: Use when opening, auditing, or closing work in an SGDK project that has or should have doc/agent_learning passive local learning context.
---

# Project Learning Loop

Use esta skill para manter aprendizado local por projeto de forma passiva, consultiva e honesta.

## Principio

`doc/agent_learning/` e memoria local do projeto. Ela informa agentes futuros, mas nao altera a `.agent` canonica, skills, workflows, `lib_case`, registry ou regras globais.

Promocao para o agente canonico so acontece por ato humano deliberado, com revisao explicita e edicao controlada na fonte canonica.

## Quando usar

- Ao abrir um projeto SGDK existente.
- Ao criar projeto novo a partir dos templates canonicos.
- Ao encerrar uma tarefa que gerou aprendizado reutilizavel, falha recorrente ou candidato de skill.
- Ao auditar se um projeto possui contexto local de aprendizado.

## Ordem de leitura

1. `doc/agent_learning/README.md`
2. `doc/agent_learning/success_patterns.md`
3. `doc/agent_learning/failure_patterns.md`
4. `doc/agent_learning/skill_promotion_candidates.md`
5. `doc/agent_learning/canonical_promotion_review.md`

Se a pasta nao existir, registre `learning_context_absent` como warning. Nao bloqueie projeto legado so por isso.

Se a pasta existir, mas faltar arquivo minimo, registre `learning_context_incomplete` e liste o que falta.

## Classificacoes

Use apenas estes valores:

- `local_note`: observacao util para este projeto.
- `promotion_candidate`: candidato local para revisao futura, ainda nao canonico.
- `do_not_promote`: aprendizado especifico, fragil ou inadequado para promocao.
- `needs_human_review`: exige decisao humana antes de qualquer uso canonico.

## Registro ao fechar tarefa

Registre apenas o que foi observado na execucao real:

- padroes de sucesso comprovados em `success_patterns.md`;
- falhas e mitigacoes em `failure_patterns.md`;
- possiveis skills ou workflows em `skill_promotion_candidates.md`;
- pendencias de decisao em `canonical_promotion_review.md`.

Vincule evidencias quando existirem: build, `validation_report.json`, screenshot BlastEm, hash, log ou caminho de artefato.

## Proibicoes

- Nao promova automaticamente nada para `.agent`.
- Nao edite skills canonicas por inferencia local.
- Nao atualize registry, `lib_case` ou workflow canonico sem ordem humana explicita.
- Nao trate ausencia de `doc/agent_learning/` em projeto legado como falha de entrega.
- Nao confunda `out/agent_learning/` com memoria versionavel.

## Saida esperada

Todo uso desta skill deve deixar claro:

- status de contexto: `learning_context_present`, `learning_context_absent` ou `learning_context_incomplete`;
- se algum registro local foi atualizado;
- se ha candidato pendente de revisao humana;
- confirmacao de que nenhuma promocao canonica automatica ocorreu.

