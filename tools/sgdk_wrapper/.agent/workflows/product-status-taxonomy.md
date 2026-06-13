# Workflow: Product Status Taxonomy

Contrato canonico para separar laboratorio tecnico, fatia jogavel e entrega AAA.

Regra base: lab comprovado prova capacidade tecnica. Produto piloto fechado prova maturidade de producao. Um status mais alto nunca herda automaticamente de um status mais baixo.

## Status

| Status | Significado | Evidencia minima | Nao prova |
|---|---|---|---|
| `technical_lab_validated` | ROM ou lab tecnico compila, roda e tem evidencia tecnica rastreavel. | build, validator limpo ou bloqueios documentados, BlastEm quando aplicavel, budget/metricas do eixo tecnico medido. | direcao criativa, loop completo, maturidade de jogo, pipeline de produto. |
| `vertical_slice_candidate` | Ha loop jogavel, arte intencional, audio funcional, GDD substancial e rota clara de produto. | cena jogavel com entrada real, front-end minimo, plano de fases, plano de arte/audio, QA por marco e evidencia BlastEm do slice vigente. | polimento AAA final, conteudo completo, todos os eixos de producao fechados. |
| `ready_for_aaa` | Produto ou fatia de entrega passou por gates tecnicos, criativos, perceptivos, semanticos e de evidencia. | `technical_ready=true`, `creative_ready=true`, `perceptual_quality=measured`, `capture_status=complete`, semantic audit passed, BlastEm gate, evidencia por eixo, memoria operacional atualizada. | Nada fora do escopo declarado; se o escopo for so lab, o claim fica limitado ao lab. |

## Guardas de promocao

- `technical_lab_validated` pode virar `vertical_slice_candidate` somente quando existir loop jogavel com objetivo, falha, feedback, front-end simples, audio e plano de produto.
- `vertical_slice_candidate` pode virar `ready_for_aaa` somente quando os gates criativo, visual, audio, semantico, budget, performance e captura estiverem completos para o escopo declarado.
- Nenhum projeto com `lab_not_delivery=true`, `procedural/debug_as_final`, `perceptual_quality=nao_medido`, `capture_status!=complete` ou `blocking_statuses` nao vazio pode declarar `ready_for_aaa`.
- `ready_for_aaa` em uma cena nao significa `ready_for_aaa` do jogo inteiro. O claim deve trazer `scope_id`.
- Relatorio executivo deve mostrar `product_status`, `scope_id`, `evidence_scope`, `blocking_statuses`, `next_product_gate` e `claim_ceiling`.

## Campos recomendados

```text
product_status: technical_lab_validated | vertical_slice_candidate | ready_for_aaa
scope_id: <projeto|cena|fase|piloto>
claim_ceiling: <maximo status permitido pelo escopo atual>
technical_ready: true|false
creative_ready: true|false
perceptual_quality: measured|estimated|nao_medido
capture_status: complete|partial|missing|stale
semantic_audit_status: passed|warn|blocked|not_applicable
blastem_gate: passed|failed|not_run
evidence_axes: build, validation_report, boot_emulador, gameplay_basico, performance, audio, memoria_operacional
```

## Aplicacao em projetos piloto

Um piloto canonico deve nascer como `vertical_slice_candidate` ate provar:

- front-end simples com menu/pause;
- 3 fases curtas com progressao;
- 1 boss que reutiliza regras do jogo;
- 1 cutscene curta com FSM e teardown;
- trilha e SFX autorais ou contrato claro de audio final;
- plano de QA com evidencia BlastEm por marco;
- GDD, spec de cenas, roadmap, arte, audio, level design e criterio de aceite.

## Integracao pendente

Em 2026-06-01, os arquivos centrais `SGDK_GLOBAL.md`, `aaa-scene-pipeline.md` e `doc/06_AI_MEMORY_BANK.md` estavam modificados no worktree. A integracao direta deve seguir a proposta em `doc/agent_learning/pending_integration/product_status_taxonomy_patch.md`.
