# Workflow: Project Learning Loop

Use este fluxo para consultar e registrar aprendizado local passivo de um projeto SGDK.

O objetivo e preservar memoria util sem canonizar automaticamente comportamento, regra, skill, `lib_case` ou registry.

---

## Passo 0. Classificar o contexto

Audite `doc/agent_learning/` no projeto atual.

Status possiveis:

- `learning_context_present`: pasta existe e contem todos os arquivos minimos.
- `learning_context_absent`: pasta nao existe; warning para projeto legado, nao blocker.
- `learning_context_incomplete`: pasta existe, mas faltam arquivos minimos.

Arquivos minimos:

- `README.md`
- `success_patterns.md`
- `failure_patterns.md`
- `skill_promotion_candidates.md`
- `canonical_promotion_review.md`

Nunca crie, promova ou edite artefatos canonicos durante esta auditoria.

---

## Passo 1. Abertura do projeto

Quando `learning_context_present`:

1. leia `README.md`;
2. extraia padroes uteis de `success_patterns.md`;
3. extraia riscos de `failure_patterns.md`;
4. identifique candidatos pendentes em `skill_promotion_candidates.md`;
5. respeite bloqueios e revisoes em `canonical_promotion_review.md`.

Quando `learning_context_absent`:

- declare warning curto;
- continue pela hierarquia de verdade normal;
- nao degrade o projeto automaticamente.

Quando `learning_context_incomplete`:

- liste os arquivos ausentes;
- use os arquivos existentes como contexto parcial;
- nao assuma que o aprendizado local esta completo.

---

## Passo 2. Registro ao encerrar tarefa

Registre aprendizado somente quando houver valor futuro claro.

Use:

- `success_patterns.md` para padroes comprovados;
- `failure_patterns.md` para falhas, causas e mitigacoes;
- `skill_promotion_candidates.md` para candidatos reutilizaveis;
- `canonical_promotion_review.md` para itens que exigem decisao humana.

Cada registro deve informar:

- data;
- classificacao;
- contexto;
- evidencia ou ausencia honesta de evidencia;
- limite de uso;
- proximo criterio de revisao, quando aplicavel.

---

## Passo 3. Promocao canonica

Promocao local para canonico e proibida por padrao.

So pode ocorrer quando um humano solicitar explicitamente a assimilacao do aprendizado. Mesmo nesse caso, o agente deve:

1. comparar contra `SGDK_GLOBAL.md`;
2. verificar conflito com workflows e skills existentes;
3. verificar headers SGDK 2.11 quando envolver API;
4. escrever mudanca canonica controlada;
5. registrar decisao humana em `canonical_promotion_review.md`.

---

## Passa quando

- o status de contexto foi declarado;
- projetos legados sem pasta foram tratados como warning;
- registros locais, quando feitos, ficaram em `doc/agent_learning/`;
- nenhuma promocao automatica ocorreu;
- handoff informa candidatos pendentes de revisao humana.

---

## Handoff

Ao encerrar a sessao, declare:

- `learning_context_status`;
- arquivos locais atualizados;
- candidatos de promocao pendentes;
- confirmacao: `canonical_promotion_performed=false`, exceto quando houver ordem humana explicita e registrada.

