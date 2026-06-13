---
name: sgdk-code-reviewer
description: Use para revisão formal de código C SGDK 2.11 antes de entrega, PR, merge, fechamento AAA ou quando houver mudanças em runtime, assets .res, VBlank, DMA, input, save, região, audio ou cena. Prioriza bugs, regressões, APIs erradas, ownership, budget e ausência de testes/evidência.
---

# SGDK Code Reviewer

Esta skill cria o gate de revisão formal que faltava entre "compila" e "pode ser entregue".

## Contrato Operacional

### Entrada minima

- diff ou lista de arquivos alterados
- `src/`, `res/resources.res` e builders tocados
- `validation_report.json`
- `runtime_decision_log` quando houver runtime
- `doc/13-spec-cenas.md` e `doc/10-memory-bank.md`

### Saida minima

- `code_review_report`
- achados ordenados por severidade
- linhas/arquivos afetados
- decisao: `review_passed`, `review_passed_with_risk` ou `review_blocked`

### Passa quando

- nao ha uso de API SGDK inventada ou versao errada
- nao ha `float`, heap no loop, DMA fora de VBlank ou owner duplicado de H-Int/WINDOW/CRAM/audio
- scene manager, input, save e region contracts nao foram burlados quando aplicaveis
- `.res`, assets e runtime concordam com o budget
- evidencias usadas nao estao stale

### Handoff para proxima etapa

- entregar `code_review_report` ao validator/closeout e registrar bloqueios no memory bank

## Regras

- Review formal e obrigatorio para `AAA`, `stable`, `release`, `ready_for_aaa=true` ou projeto piloto.
- Build limpo nao substitui review.
- Review deve liderar com bugs, riscos, regressao e missing tests; estilo so entra depois.
- Se o workspace global estiver sujo, revisar apenas o escopo declarado e exigir `workspace_scope_isolation=true`.

## Anti-padroes

- aprovar porque a ROM abriu uma vez
- revisar so o arquivo que quebrou o build
- ignorar `resources.res`, builders e evidencia
- aceitar "funciona no meu emulador" sem hash e scene id
