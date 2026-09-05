# Failure Patterns

Registre aqui falhas, falsos positivos, tentativas ruins e decisoes que nao devem ser repetidas sem nova evidencia.

| Data | Classificacao | Contexto | Falha observada | Causa provavel | Mitigacao | Evidencia |
|---|---|---|---|---|---|---|
| [DATA] | `local_note` | [cena/sistema] | [o que falhou] | [causa] | [como evitar] | [log/screenshot/hash] |
| 2026-07-20 | `needs_human_review` | evidencia visual | Uma captura quase branca foi aceita inicialmente como evidencia suficiente de runtime. | O gate conferia presenca/hash do arquivo, mas nao verificava informacao visual minima nem limitava os claims derivados. | Exigir gate semantico de screenshot e reconciliar visual, gameplay e performance pelo menor status comprovado. | `out/evidence/stale/scene2_capture_20260627_225407/screenshot.png`; `doc/10-memory-bank.md` |
| 2026-07-20 | `local_note` | telemetria de performance | Uma janela curta de 32 amostras podia parecer estavel sem representar uma janela regional completa. | O probe nao tinha alvo regional, flag explicita de conclusao nem contrato de captura parcial. | Exigir alvo configuravel, contagem completa e `probe_window_complete`; captura parcial permanece `unproven`. | `out/evidence/blastem/runtime_metrics_mdrt.json`; `out/evidence/blastem_pal/runtime_metrics_mdrt.json`; `out/logs/performance_capture_report.json` |
| 2026-07-20 | `needs_human_review` | exportacao SRAM | O heartbeat continuava escrevendo depois da exportacao e podia corromper a serie de performance ja selada. | Dois produtores compartilhavam a mesma regiao de SRAM sem ownership temporal pos-exportacao. | Selar a janela somente quando completa e impedir qualquer escrita concorrente sobre o payload exportado. | `out/evidence/blastem/save.sram`; `out/logs/performance_capture_report.json`; `doc/10-memory-bank.md` |
| 2026-07-20 | `needs_human_review` | continuidade documental | Memory bank, changelog e reports podem manter hashes ou status de momentos diferentes. | Relatorios mutaveis e narrativas historicas nao tinham um auditor unico de identidade e status ativo. | Executar `doc_sync_audit` antes de handoff forte; report stale nao pode permanecer como claim ativo. | `doc/10-memory-bank.md`; `doc/changelog/changelog.md` |
| 2026-07-20 | `local_note` | escopo de validacao | BlastEm e metricas tecnicas poderiam ser interpretados como prova de audio, hardware real, qualidade criativa ou jogo completo. | Claims distintos estavam proximos no mesmo closeout sem uma fronteira explicita por eixo. | Registrar status por eixo e manter hardware, audio humano, visual e release bloqueados ate evidencia propria. | `out/logs/hardware_test_gate_report.json`; `doc/10-memory-bank.md` |

## Regras

- Falha sem evidencia deve ser marcada como hipotese.
- Solucao nao comprovada nao vira recomendacao.
- Se a falha indicar risco canonico, classifique como `needs_human_review`.
