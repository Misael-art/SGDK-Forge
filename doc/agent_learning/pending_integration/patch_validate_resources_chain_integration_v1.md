# PATCH PENDENTE: tools/sgdk_wrapper/validate_resources.ps1

> **Status**: worktree sujo preexistente (HEAD = 3496 linhas; working = ~7000+ linhas).  
> **Origem**: Game Systems Pipeline Hardening (2026-06-01).  
> **Acao humana necessaria**: revisar `git diff` no arquivo e aplicar este patch quando o worktree for limpo.  
> **Aplicar apos**: resolver os 1658+ linhas de diff ja presentes em validate_resources.ps1 (sem relacao com este patch).  
> **Pre-requisito de leitura**: o script ja implementa `product_status` e `claim_ceiling` (confirmado em leituras anteriores). Este patch adiciona apenas a integracao opcional com o novo `audit_game_design_contracts.ps1`.

---

## Patch: chamar audit_game_design_contracts.ps1 no final do validate_resources.ps1

Adicionar no final do fluxo principal (depois do report final de `validation_report.json` ja existente), uma chamada opcional ao novo auditor, somente quando o `product_status` for `vertical_slice_candidate` ou `ready_for_aaa` e houver contratos de design no projeto.

```powershell
# === BEGIN GAME_PRODUCTION_CHAIN_INTEGRATION (2026-06-01) ===
# Integracao opcional com audit_game_design_contracts.ps1.
# Quando o projeto alvo eh vertical_slice_candidate ou ready_for_aaa
# e existem contratos de design em doc/contracts/ ou similar,
# chama o auditor e anexa o resultado a validation_report.json.

$auditScript = Join-Path $PSScriptRoot 'audit_game_design_contracts.ps1'
if (Test-Path -LiteralPath $auditScript) {
    $contractsRoot = Join-Path $ProjectRoot 'doc\contracts'
    $gddDir = if (Test-Path -LiteralPath $contractsRoot) { $contractsRoot } else { $ProjectRoot }
    $mechPath = Get-ChildItem -Path $gddDir -Filter 'mechanic_contract.json' -ErrorAction SilentlyContinue | Select-Object -First 1
    $lvlPath = Get-ChildItem -Path $gddDir -Filter 'level_blueprint.json' -ErrorAction SilentlyContinue | Select-Object -First 1
    $enemyPath = Get-ChildItem -Path $gddDir -Filter 'enemy_roster.json' -ErrorAction SilentlyContinue | Select-Object -First 1
    $tddPath = Get-ChildItem -Path $gddDir -Filter 'tdd_contract.json' -ErrorAction SilentlyContinue | Select-Object -First 1

    if ($mechPath -or $lvlPath -or $enemyPath -or $tddPath) {
        $auditOut = Join-Path $auditDir 'audit_game_design_contracts_report.json'
        $auditArgs = @{
            ProductStatus = $resolvedProductStatus
            OutputPath = $auditOut
            WrapperRoot = $PSScriptRoot
        }
        if ($mechPath) { $auditArgs['MechanicContractPath'] = $mechPath.FullName }
        if ($lvlPath) { $auditArgs['LevelBlueprintPath'] = $lvlPath.FullName }
        if ($enemyPath) { $auditArgs['EnemyRosterPath'] = $enemyPath.FullName }
        if ($tddPath) { $auditArgs['TddContractPath'] = $tddPath.FullName }
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $auditScript @auditArgs 2>&1 | ForEach-Object { Write-Host "[validate_resources] $_" }
        if (Test-Path -LiteralPath $auditOut) {
            $auditReport = Get-Content -LiteralPath $auditOut -Raw -Encoding UTF8 | ConvertFrom-Json
            $validationReport.audit_game_design_contracts = @{
                status = [string]$auditReport.status
                blocking_statuses = @($auditReport.blocking_statuses)
                catalog_checks = $auditReport.catalog_checks
                cross_references = $auditReport.cross_references
            }
            if ($auditReport.status -eq 'blocked') {
                $validationReport.status = 'blocked'
                $validationReport.blocking_statuses += 'audit_game_design_contracts_blocked'
            }
        }
    }
}
# === END GAME_PRODUCTION_CHAIN_INTEGRATION ===
```

---

## Variaveis esperadas (ja existentes no script)

- `$PSScriptRoot` ja eh o diretorio do `validate_resources.ps1` (padrao).
- `$ProjectRoot` ja existe e eh a raiz do projeto sendo validado.
- `$resolvedProductStatus` ja existe (variavel canonica de `product_status`).
- `$auditDir` ja existe como `out/logs/` (ou equivalente).
- `$validationReport` ja eh o objeto final antes de `ConvertTo-Json`.

## Comportamento esperado

1. Se o projeto for lab (`technical_lab_validated`), nao chama o auditor (gate eh opcional).
2. Se nenhum contrato de design existir, nao chama o auditor (gate eh opcional).
3. Se o auditor retornar `status=blocked`, o `$validationReport.status` vira `blocked` e adiciona o codigo `audit_game_design_contracts_blocked` em `blocking_statuses`.
4. Se o auditor retornar `status=warn`, o `$validationReport.status` vira `warn` (sem mexer em `blocking_statuses`).
5. Se o auditor retornar `status=passed`, nao altera `$validationReport.status`.

## Validacao esperada apos aplicacao

- `pwsh -File tools/sgdk_wrapper/ci/test_game_design_contract_gates.ps1` continua com 19/19 PASS.
- `pwsh -File tools/sgdk_wrapper/validate_resources.ps1 -ProjectRoot <algum projeto>` continua gerando `out/logs/validation_report.json`.
- Para projeto com contratos em `doc/contracts/`, `validation_report.json` agora contem bloco `audit_game_design_contracts`.
- Para projeto sem contratos, `validation_report.json` NAO contem o bloco (sem regressao).
- O test runner do wrapper continua passando (validate_resources.ps1 eh parte do CI local).
- O numero de linhas cresce em ~45 linhas.
