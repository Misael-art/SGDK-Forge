# Workflow: Handoff

Use este fluxo ao encerrar uma sessao relevante.

1. Resuma o que mudou de fato.
2. Registre o que continua placeholder ou parcial.
3. Atualize o artefato canonico de memoria operacional do contexto: `doc/10-memory-bank.md` no projeto ou `doc/06_AI_MEMORY_BANK.md` no workspace.
4. Declare o que foi buildado, o que foi testado em BlastEm e o que so tem evidência complementar de BizHawk/telemetria.
5. Liste os artefatos de evidencia produzidos: `validation_report.json`, `runtime_metrics.json`, logs, screenshots e hashes relevantes.
6. Se houver deriva documental ou divergencia da `.agent`, nao a esconda.
7. Diferencie explicitamente `visual_lab_aprovado`, `gameplay_rom_aprovada` e `ready_for_aaa` quando o contexto tiver viewer/lab visual.

## Schema minimo de handoff

Todo handoff entre Director, Art, Code e QA deve declarar explicitamente:

- `de`: papel que entrega
- `para`: papel que recebe
- `objetivo`: recorte exato da iteracao
- `entradas`: docs canonicos, assets, hashes e manifests usados
- `saidas`: codigo, assets, ROM, reports e logs gerados
- `status_por_eixo`: `documentado`, `implementado`, `buildado`, `testado_em_emulador`, `validado_budget`, `placeholder`, `parcial`, `futuro_arquitetural`
- `bloqueios`: riscos, gaps de evidencia e pendencias reais
- `proximo_gate`: criterio objetivo para a proxima etapa aceitar a entrega
