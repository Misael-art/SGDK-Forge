# Success Patterns

Registre aqui apenas padroes que funcionaram neste projeto com evidencia rastreavel.

| Data | Classificacao | Contexto | Padrao observado | Evidencia | Limite de uso |
|---|---|---|---|---|---|
| [DATA] | `local_note` | [cena/sistema] | [o que funcionou] | [build/log/screenshot/hash] | [onde nao aplicar] |
| 2026-07-20 | `local_note` | performance cena 3 | Janela completa e selada por regiao, com serie bruta e agregados reconciliados, sustentou o claim de estabilidade apenas no recorte observado. | `out/evidence/blastem/runtime_metrics_mdrt.json`; `out/evidence/blastem_pal/runtime_metrics_mdrt.json`; `out/logs/performance_budget_report.json` | Nao generalizar para outras cenas, audio, hardware, jogo completo ou release. |
| 2026-07-20 | `local_note` | evidencia BlastEm | ROM, SRAM, screenshot, metricas e identificador de sessao no mesmo bundle reduziram ambiguidade e permitiram auditar frescor. | `out/evidence/blastem/evidence_manifest.json`; `out/evidence/blastem/freshness_report.json`; `out/evidence/blastem/screenshot.png` | Um bundle coerente ainda nao prova automaticamente gameplay amplo, qualidade visual ou audio. |
| 2026-07-20 | `local_note` | compatibilidade regional | Capturas NTSC e PAL separadas, com regiao observada e metas distintas, evitaram inferir PAL a partir de uma sessao NTSC. | `out/evidence/blastem/session_runtime.json`; `out/evidence/blastem_pal/session_runtime.json`; `out/evidence/blastem_pal/freshness_report.json` | Nao substitui console real ou FPGA e nao cobre todas as cenas. |
| 2026-07-20 | `local_note` | gate externo | Um manifesto de hardware pendente e um validador bloqueante preservaram a verdade quando nao havia console, FPGA, video ou atestacao. | `out/logs/hardware_test_gate_report.json`; `doc/hardware_test_protocol.md` | O gate implementado nao equivale a uma sessao fisica executada. |
| 2026-07-20 | `local_note` | decisao conservadora | Limitar cada conclusao ao menor escopo comprovado permitiu fechar P1-003 sem promover visual, audio, hardware ou AAA. | `doc/10-memory-bank.md`; `doc/changelog/changelog.md` | Nao usar a decisao conservadora para esconder blockers ou deixar reports stale sem reconciliacao. |

## Regras

- Nao transforme sucesso local em regra global.
- Nao registre preferencia estetica como skill tecnica.
- Nao use este arquivo para alterar `.agent`, registry ou `lib_case`.
