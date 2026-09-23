# Changelog de Curadoria Canonica - 2026-06-20

## Verificacao e robustez operacional

- Corrigida compatibilidade do auditor de lifecycle com Windows PowerShell 5.1.
- Corrigido `default_gate` do route map para `aaa-pipeline-guardian`.
- Graphify agora rejeita update/build quando o processo externo retorna erro e
  nao grava snapshot de freshness falso.
- Adicionada regressao para recusa de update Graphify.
- O runner global de contratos usa `uv run --with jsonschema`, eliminando
  dependencia de pacote Python global.
- Guards de promocao por genero foram alinhados ao registry v3: validam
  `active/deferred`, opt-in explicito e ausencia de `MESTRE_*`, sem depender
  do campo legado `promotion_tier` por entrada.
- Wrappers de registry nao tratam mais `$LASTEXITCODE = null` como falha.
- Removidos estados contraditorios de runner bloqueado da memoria operacional
  atual; o incidente permanece apenas como historico.

## Evidencia

- curadoria canonica: passed;
- lifecycle reversivel: passed;
- projeto learning loop: 33/33;
- schemas: 73/73;
- startup/Graphify: 28/28;
- Graphify update failure regression: passed.
- `run_all_contract_gates.ps1 -Mode smoke`: `combined_status=passed`.

Status: `validated_framework_no_rom`.
