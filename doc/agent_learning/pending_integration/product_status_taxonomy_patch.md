# Pending Integration: Product Status Taxonomy

Data: 2026-06-01
Motivo: `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md`, `tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md` e `doc/06_AI_MEMORY_BANK.md` estavam modificados no worktree antes desta rodada. Para evitar sobrescrever trabalho de outro agente, esta proposta registra o patch sem editar esses arquivos diretamente.

## Objetivo

Separar formalmente:

- `technical_lab_validated`
- `vertical_slice_candidate`
- `ready_for_aaa`

Regra executiva: labs comprovam capacidade tecnica; somente um piloto fechado comprova maturidade de producao.

## Proposta para `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md`

Inserir apos a secao de governanca/status:

```md
### Taxonomia de status de produto

- `technical_lab_validated`: ROM/lab tecnico compila, roda e possui evidencia tecnica rastreavel. Nao prova direcao criativa, loop completo ou maturidade de produto.
- `vertical_slice_candidate`: existe loop jogavel com front-end minimo, arte intencional, audio funcional, GDD substancial, rota de produto, QA por marco e evidencia BlastEm do slice vigente. Ainda pode falhar em polimento AAA ou conteudo completo.
- `ready_for_aaa`: escopo declarado possui `technical_ready=true`, `creative_ready=true`, `perceptual_quality=measured`, `capture_status=complete`, semantic audit passed, BlastEm gate, evidencia por eixo, memoria operacional atualizada e jogo demonstravel.

`ready_for_aaa` sempre exige `scope_id`. Um lab ou cena pode estar fechado no proprio escopo sem promover o jogo inteiro. `lab_not_delivery=true`, procedural/debug como final, `perceptual_quality=nao_medido`, `capture_status!=complete` ou `blocking_statuses` nao vazio bloqueiam o claim.
```

## Proposta para `tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md`

Inserir antes de `Dependencias Fixas`:

```md
## Gate de produto

Antes do fechamento, classifique `product_status`:

- `technical_lab_validated` para labs/eixos tecnicos com ROM, budget e evidencia, mas sem loop de produto.
- `vertical_slice_candidate` para fatia jogavel com loop, front-end minimo, arte/audio intencionais, GDD/spec substanciais e roadmap executavel.
- `ready_for_aaa` somente quando `technical_ready`, `creative_ready`, `perceptual_quality=measured`, `capture_status=complete`, semantic audit, BlastEm gate e evidencia por eixo estiverem completos para o `scope_id`.

Se o escopo for uma campanha de labs, o teto padrao e `technical_lab_validated`. Se o escopo for piloto jogavel, o teto inicial e `vertical_slice_candidate` ate haver produto demonstravel com todos os gates.
```

## Proposta para `doc/06_AI_MEMORY_BANK.md`

Adicionar novo bloco ao final:

```md
## CURADORIA 2026-06-01 - TAXONOMIA DE PRODUTO

Status: `pending_integration`.

Foi proposta a taxonomia `technical_lab_validated`, `vertical_slice_candidate` e `ready_for_aaa` para impedir que labs tecnicos sejam promovidos a produto completo. A fonte operacional nova e `tools/sgdk_wrapper/.agent/workflows/product-status-taxonomy.md`.

Decisao: `ready_for_aaa` passa a exigir `scope_id`, `technical_ready`, `creative_ready`, `perceptual_quality=measured`, `capture_status=complete`, semantic audit passed, BlastEm gate e evidencia por eixo. Um slice pode fechar seu proprio escopo sem provar que o jogo completo esta maduro.
```

## Campos recomendados para validators e reports futuros

```text
product_status
scope_id
claim_ceiling
technical_ready
creative_ready
perceptual_quality
capture_status
semantic_audit_status
blastem_gate
evidence_axes
blocking_statuses
next_product_gate
```

## Decisao conservadora

Nao houve edicao direta dos tres arquivos centrais por risco de conflito com a rodada paralela de hardening de gates.
