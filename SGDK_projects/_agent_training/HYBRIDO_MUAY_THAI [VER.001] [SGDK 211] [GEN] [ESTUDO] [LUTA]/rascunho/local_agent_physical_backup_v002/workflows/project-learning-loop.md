# Workflow: Project Learning Loop

Use este fluxo na abertura e no fechamento de trabalho relevante em projetos SGDK.

O agente aprende automaticamente dentro do projeto. O cânone nunca é alterado automaticamente.

---

## Passo 0. Materializar sem sobrescrever

Execute:

```powershell
tools/sgdk_wrapper/adopt_project_methodology.ps1 -ProjectRoot <projeto> -Lifecycle <new|existing|reseed>
```

Projetos antigos recebem arquivos ausentes de `doc/agent_learning/` sem sobrescrever decisões ou registros existentes.

---

## Passo 1. Abertura read-only

Execute:

```powershell
tools/sgdk_wrapper/audit_project_learning.ps1 -ProjectRoot <projeto> -Mode Audit -OutputFormat Json
```

Regras:

- ausência em legado é warning, não blocker;
- leia primeiro `candidate_index`;
- carregue a lição completa do ledger somente se ela for relevante à tarefa;
- não escreva ou promova nada durante `Audit`.

---

## Passo 2. Registrar observações reais

Atualize os Markdown locais somente com fatos observados:

- `success_patterns.md`: sucesso com evidência;
- `failure_patterns.md`: falha, diagnóstico e prevenção;
- `skill_promotion_candidates.md`: gap procedural possivelmente reutilizável;
- `canonical_promotion_review.md`: decisão ou pendência humana.

Falha sem solução comprovada continua falha. Preferência estética isolada não vira skill.

---

## Passo 3. Captura automática local

Após build, validações e evidências relevantes:

```powershell
tools/sgdk_wrapper/audit_project_learning.ps1 -ProjectRoot <projeto> -Mode Capture -OutputFormat Json
```

O comando:

1. extrai lições dos registros locais;
2. vincula apenas evidências internas reconhecidas;
3. rejeita caminhos externos;
4. gradua evidência e freshness;
5. procura owner canônico existente;
6. gera propostas `not_applied`;
7. atualiza o ledger local e o report runtime.

Arquivos permitidos:

- `doc/agent_learning/learning_ledger.json`;
- `out/logs/project_learning_report.json`.

---

## Passo 4. Revisão canônica

Nenhuma proposta local autoriza patch.

Para alterar o cânone, exigir:

1. pedido ou aprovação humana explícita;
2. evidência adequada e fresca;
3. deduplicação confirmada;
4. teste de generalização;
5. proposta de diff e riscos;
6. aplicação controlada;
7. regressão completa;
8. registro da decisão humana.

---

## Passa quando

- `Audit` não modificou arquivos;
- `Capture` escreveu somente dentro do projeto;
- candidatos conhecidos apontam para owners existentes;
- skill nova aparece apenas como proposta pendente;
- captura repetida sem mudanca semantica preserva o ledger byte a byte;
- nenhuma proposta está aplicada;
- `canonical_promotion_performed=false`.

---

## Handoff

Declarar:

- `learning_context_status`;
- quantidade de lições e candidatos;
- gaps de evidência;
- propostas pendentes;
- `canonical_promotion_performed=false`.
