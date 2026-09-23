# Canonical Promotion Review

Use este arquivo para revisar, com cautela, se algum aprendizado local deve ser levado para o framework canonico.

## Politica

Promocao canonica so ocorre quando um humano ordenar explicitamente a assimilacao. Ate la, tudo permanece local e passivo.

## Checklist de revisao

| Item | Status |
|---|---|
| O aprendizado tem evidencia rastreavel? | [pendente] |
| O padrao funcionou fora de um caso unico? | [pendente] |
| Os riscos e limites estao escritos? | [pendente] |
| Existe conflito com `SGDK_GLOBAL.md`? | [pendente] |
| Existe conflito com headers SGDK 2.11? | [pendente] |
| Um humano aprovou a promocao? | [pendente] |

## Decisoes

| Data | Candidato | Decisao | Justificativa | Autor humano |
|---|---|---|---|---|
| [DATA] | [candidato] | `needs_human_review` | [motivo] | [nome/handle] |
| 2026-07-20 | screenshot_semantic_and_claim_floor | `verified_existing_canonical_mechanism` | Gate semantico e reconciliacao conservadora ja possuem implementacao e regressao; manter monitoramento, sem criar skill duplicada. | usuario_workspace_owner |
| 2026-07-20 | same_session_evidence_identity | `verified_existing_canonical_mechanism` | Bundle por ROM, sessao e frescor ja esta integrado; revalidar em todo rebuild. | usuario_workspace_owner |
| 2026-07-20 | configurable_full_window_runtime_probe | `needs_human_review` | Prova local NTSC/PAL e forte, mas generalizacao exige segundo projeto e parametros em vez de constantes do BLUE CIRCUIT. | usuario_workspace_owner |
| 2026-07-20 | sealed_sram_export_ownership | `needs_human_review` | Correcao local funcionou; falta contrato geral de ownership e fixture de corrupcao concorrente. | usuario_workspace_owner |
| 2026-07-20 | hardware_evidence_adoption_gate | `needs_human_review` | Gate tecnico existe, mas nenhuma sessao externa valida foi fornecida. | usuario_workspace_owner |
| 2026-07-20 | doc_claim_sync_audit | `resume_when_p2_001_verified` | Auditor e regressao foram iniciados; falta report real coerente e fechamento do backlog. | usuario_workspace_owner |
| 2026-07-20 | independent_session_context_recovery | `resume_after_doc_sync` | A retomada independente depende de fontes sincronizadas e ainda nao foi medida. | usuario_workspace_owner |

## Estado De Maturidade Para Retomada

| Ponto | Estado atual | O que ja existe | O que falta | Gatilho de retomada |
|---|---|---|---|---|
| Evidencia visual semantica | `integrado_verificado` | Gate, schema, fixtures negativas e consumo no closeout | Monitorar regressao | Nova falha semantica ou mudanca do formato de captura |
| Menor claim comprovado | `integrado_verificado` | Reconciliador e bloqueios por conflito/identidade | Integrar novos tipos de report quando surgirem | Novo report com claim forte nao reconhecido |
| Bundle fresco da mesma sessao | `integrado_verificado` | ROM, SRAM, screenshot, metricas, sessao e freshness | Reexecutar depois de cada ROM | Rebuild, nova captura ou mudanca de contrato |
| Performance de janela completa | `comprovado_localmente` | NTSC 900/900 e PAL 750/750 na cena 3 | Segundo projeto/cena e parametrizacao canonica | Evidencia cross-project reproduzivel |
| Ownership da SRAM selada | `comprovado_localmente` | Heartbeat desativado depois do selo | Contrato geral de offsets e teste concorrente | Fixture que reproduza corrupcao e passe apos a correcao |
| Hardware real/FPGA | `gate_implementado_bloqueado_externo` | Protocolo, schema, validador e fixture | Sessao real, captura e atestacao | Evidencia externa vinculada a mesma ROM |
| Sincronizacao memoria/reports | `em_andamento` | Auditor e regressao iniciais | Executar report real e fechar P2-001 | `doc_sync_report` sem contradicoes fortes |
| Retomada independente | `nao_executado` | Memory bank, changelog e backlog | Sessao independente e context recovery report | P2-001 concluido |
| Curadoria canonica adicional | `pausada_aguardando_maturidade` | Candidatos, owners sugeridos e criterios | Generalizacao, regressao e nova aprovacao por patch | Cada candidato cumprir seu gatilho acima |
