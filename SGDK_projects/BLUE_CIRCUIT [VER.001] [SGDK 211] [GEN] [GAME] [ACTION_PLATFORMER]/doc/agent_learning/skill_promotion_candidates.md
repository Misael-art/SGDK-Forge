# Skill Promotion Candidates

Este arquivo lista candidatos locais que talvez merecam virar skill, workflow, regra, script ou `lib_case` canonico no futuro.

Nenhum item aqui esta promovido.

| Data | Classificacao | Candidato | Problema resolvido | Evidencia minima | Risco | Proxima revisao humana |
|---|---|---|---|---|---|---|
| [DATA] | `promotion_candidate` | [nome curto] | [problema] | [build/log/screenshot/hash] | [baixo/medio/alto] | [criterio] |
| 2026-07-20 | `promotion_candidate` | doc_claim_sync_audit | Evitar contradicao forte entre ROM, status gerado, memoria, changelog e reports ativos. | `doc/10-memory-bank.md`; `doc/changelog/changelog.md` | alto | Retomar apos P2-001 gerar `out/logs/doc_sync_report.json` real e a regressao bloquear hash/status contraditorio. |
| 2026-07-20 | `promotion_candidate` | independent_session_context_recovery | Garantir que uma nova sessao encontre blocker, ROM, claim ceiling e proxima acao sem reorientacao humana. | `doc/10-memory-bank.md`; `doc/changelog/changelog.md` | medio | Retomar apos P2-001 e exigir log de sessao independente mais context recovery report sem promocao historica. |
| 2026-07-20 | `promotion_candidate` | configurable_full_window_runtime_probe | Generalizar janela completa, conclusao explicita e reconciliacao entre serie e agregados sem fixar valores de um unico jogo. | `out/evidence/blastem/runtime_metrics_mdrt.json`; `out/evidence/blastem_pal/runtime_metrics_mdrt.json`; `out/logs/performance_capture_report.json` | medio | Testar em outro projeto/cena com metas configuraveis; preservar fixture de captura parcial e regressao NTSC/PAL. |
| 2026-07-20 | `promotion_candidate` | sealed_sram_export_ownership | Impedir que heartbeat ou outro produtor altere um payload de evidencia depois do selo. | `out/evidence/blastem/save.sram`; `out/logs/performance_capture_report.json` | alto | Definir ownership de offsets, teste de corrupcao pos-exportacao e compatibilidade com probes existentes. |
| 2026-07-20 | `promotion_candidate` | hardware_evidence_adoption_gate | Fazer novos projetos que aleguem hardware/release nascerem com protocolo, manifesto e bloqueio externo proporcional. | `doc/hardware_test_protocol.md`; `out/logs/hardware_test_gate_report.json` | medio | Testar adocao em fixture nova e registrar pelo menos uma sessao externa valida antes de ampliar claims. |

## Criterios minimos

- Deve ter sido usado com sucesso em contexto real do projeto.
- Deve reduzir erro recorrente, custo de producao ou ambiguidade.
- Deve ter limites declarados.
- Deve exigir revisao humana antes de qualquer mudanca canonica.
