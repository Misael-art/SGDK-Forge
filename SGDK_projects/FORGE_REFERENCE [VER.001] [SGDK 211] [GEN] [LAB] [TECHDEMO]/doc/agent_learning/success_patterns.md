# Success Patterns

Registre aqui apenas padroes que funcionaram neste projeto com evidencia rastreavel.

| Data | Classificacao | Contexto | Padrao observado | Evidencia | Limite de uso |
|---|---|---|---|---|---|
| [DATA] | `local_note` | [cena/sistema] | [o que funcionou] | [build/log/screenshot/hash] | [onde nao aplicar] |
| 2026-08-06 | `local_note` | sete contratos de fixture | Manter gate fechado, separar os owners de SRAM e recapturar após a última mudança de ROM produziu bundle selado e cobertura ROM-side observada sem IP ou assets externos | out/evidence/forge_reference/blastem-linux-20260806T024237Z-253942/evidence_manifest.json, out/evidence/forge_reference/blastem-linux-20260806T024237Z-253942/fref_final_gate_report.json | Prova somente `technical_fixture_contracts`; nao prova audio, performance sustentada, jogo completo ou AAA |

## Regras

- Nao transforme sucesso local em regra global.
- Nao registre preferencia estetica como skill tecnica.
- Nao use este arquivo para alterar `.agent`, registry ou `lib_case`.
