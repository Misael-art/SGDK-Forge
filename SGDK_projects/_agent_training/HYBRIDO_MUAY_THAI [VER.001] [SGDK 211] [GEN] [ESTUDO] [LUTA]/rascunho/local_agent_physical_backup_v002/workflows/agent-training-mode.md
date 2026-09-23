# Agent Training Mode

Status: `canonical_workflow`

## Objetivo

Treinar o agente com pratica controlada, estudos e projetos de exercicio sem
contaminar producao ou canone.

Este modo aumenta proficiencia procedural, mas nao aplica patch canonico por
si so.

## Local Permitido

Treino vive em:

- `SGDK_projects/_agent_training/`

Projetos de treino devem:

- usar tags de nome com `[LAB]` ou `[ESTUDO]`;
- manter todo material dentro do proprio projeto;
- copiar entradas externas para `rascunho/` com hash;
- declarar `lab_not_delivery=true` ou equivalente no report;
- nunca declarar `ready_for_aaa=true`.

## Entrada

Antes de treinar:

1. confirme objetivo de aprendizado;
2. defina tecnica, skill ou workflow alvo;
3. declare se ha projeto de estudo existente ou se sera criado um fixture;
4. rode `audit_project_learning.ps1 -Mode Audit` se houver projeto base;
5. carregue primeiro o indice compacto de licoes, nao todo o historico.

## Execucao

Durante o treino:

- use skills canonicas reais;
- isole experimentos em projeto de treino;
- registre comandos, evidencia, falhas e correcoes;
- diferencie intuicao, observacao, build e emulador;
- mantenha `LABORATORIO` para tecnicas nao comprovadas em projeto aprovado.

## Captura

Ao concluir treino relevante:

```powershell
tools/sgdk_wrapper/audit_project_learning.ps1 -ProjectPath "<training_project>" -Mode Capture
```

Saidas esperadas:

- `<training_project>/doc/agent_learning/learning_ledger.json`
- licoes locais;
- propostas canonicas com status `not_applied`;
- nenhuma escrita automatica em `tools/sgdk_wrapper/.agent/`.

## Promocao

Uma licao de treino so pode virar patch canonico depois de:

1. revisao humana;
2. evidencia reprodutivel;
3. testes/validadores;
4. aprovacao explicita;
5. aplicacao via `curation-mode.md`.

## Bloqueios

Bloqueie ou rebaixe para laboratorio quando:

- a tecnica depende de claim nao testado;
- nao ha build ou report;
- a licao contradiz headers SGDK 2.11;
- o material veio de texto externo nao verificado;
- o projeto de treino tentou gravar artefato fora de si.

