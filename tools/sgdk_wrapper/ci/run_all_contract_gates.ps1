<#
.SYNOPSIS
    Orquestra todos os gates de contrato de design de jogo (auditor + schemas).

.DESCRIPTION
    Roda em sequencia:
    1. test_agent_startup_environment.ps1 (guard comum de agentes + Graphify consultivo)
    2. test_game_design_contract_gates.ps1 (auditor 3-bucket + ready flags)
    3. test_schema_contract_gates.py (jsonschema Draft-07)
    3a. test_art_gameplay_direction_gate.ps1 (gate art director + game design)
    4. test_project_context_governance.ps1 (contexto de trabalho + docs proporcionais)
    5. test_project_methodology_governance.ps1 (claims estruturados + gates)
    6. test_project_bootstrap_qaproof.ps1 (template limpo + manifests)
    7. test_freshness_audit.ps1 (drift interno propagado ao closeout)
    8. test_project_hygiene_governance.ps1 (isolamento + rascunho + copias externas)
    9. test_changelog_status_sync.ps1 (memoria derivada sem snapshot artificial)
    10. test_project_learning_loop.py (captura local + propostas sem mutacao canonica)
    11. test_genre_specialization_registry.ps1 (registry canonico v1)
    12. test_fighting_specialization_orchestrator.ps1 (orquestrador fino)
    13. test_fighting_specialization_contracts.ps1 (5 schemas + validator em fixture)
    14. test_fighting_master_promotion_guard.ps1 (sem auto-promocao MESTRE_*)
    15. test_fighting_specialization_validator_smoke.ps1 (validator no caminho generalista)
    16. test_rpg_specialization_orchestrator.ps1 (orquestrador fino rpg)
    17. test_rpg_specialization_registry.ps1 (registry rpg_turn_based_jrpg)
    18. test_rpg_specialization_contracts.ps1 (4 RPG schemas + validator em fixture)
    19. test_rpg_master_promotion_guard.ps1 (sem auto-promocao MESTRE_* rpg)
    20. test_rpg_specialization_validator_smoke.ps1 (validator rpg no caminho generalista)
    21. test_strategy_specialization_orchestrator.ps1 (orquestrador fino strategy)
    22. test_strategy_specialization_registry.ps1 (registry strategy_tower_defense)
    23. test_strategy_specialization_contracts.ps1 (4 strategy schemas + validator em fixture)
    24. test_strategy_master_promotion_guard.ps1 (sem auto-promocao MESTRE_* strategy)
    25. test_strategy_specialization_validator_smoke.ps1 (validator strategy no caminho generalista)
    26. test_brawler_specialization_orchestrator.ps1 (orquestrador fino brawler)
    27. test_brawler_specialization_registry.ps1 (registry brawler_belt_scroll)
    28. test_brawler_specialization_contracts.ps1 (4 brawler schemas + validator em fixture)
    29. test_brawler_master_promotion_guard.ps1 (sem auto-promocao MESTRE_* brawler)
    30. test_brawler_specialization_validator_smoke.ps1 (validator brawler no caminho generalista)
    31. test_platformer_specialization_orchestrator.ps1 (orquestrador fino platformer)
    32. test_platformer_specialization_registry.ps1 (registry platformer_precision_2d)
    33. test_platformer_specialization_contracts.ps1 (4 platformer schemas + validator em fixture)
    34. test_platformer_master_promotion_guard.ps1 (sem auto-promocao MESTRE_* platformer)
    35. test_platformer_specialization_validator_smoke.ps1 (validator platformer no caminho generalista)
    36. test_racing_specialization_orchestrator.ps1 (orquestrador fino racing)
    37. test_racing_specialization_registry.ps1 (registry racing_arcade)
    38. test_racing_specialization_contracts.ps1 (4 racing schemas + validator em fixture)
    39. test_racing_master_promotion_guard.ps1 (sem auto-promocao MESTRE_* racing)
    40. test_racing_specialization_validator_smoke.ps1 (validator racing no caminho generalista)

    Produz out/ci/contract_gates_report.json com:
    - agent_startup_test: { exit_code, duration_seconds, output_tail }
    - audit_test: { passed, failed, total, exit_code }
    - schema_test: { passed, failed, total, exit_code }
    - art_gameplay_direction_gate_test: { passed, failed, total, exit_code }
    - project_context_test: { exit_code, duration_seconds, output_tail }
    - methodology_test: { passed, failed, total, exit_code }
    - bootstrap_test: { passed, failed, total, exit_code }
    - freshness_test: { passed, failed, total, exit_code }
    - status_sync_test: { passed, failed, total, exit_code }
    - project_learning_test: { passed, failed, total, exit_code }
    - genre_registry_test: { exit_code, duration_seconds, output_tail }
    - fighting_orchestrator_test: { exit_code, duration_seconds, output_tail }
    - fighting_contracts_test: { exit_code, duration_seconds, output_tail }
    - fighting_master_promotion_test: { exit_code, duration_seconds, output_tail }
    - fighting_validator_smoke_test: { exit_code, duration_seconds, output_tail }
    - rpg_orchestrator_test: { exit_code, duration_seconds, output_tail }
    - rpg_registry_test: { exit_code, duration_seconds, output_tail }
    - rpg_contracts_test: { exit_code, duration_seconds, output_tail }
    - rpg_master_promotion_test: { exit_code, duration_seconds, output_tail }
    - rpg_validator_smoke_test: { exit_code, duration_seconds, output_tail }
    - strategy_orchestrator_test: { exit_code, duration_seconds, output_tail }
    - strategy_registry_test: { exit_code, duration_seconds, output_tail }
    - strategy_contracts_test: { exit_code, duration_seconds, output_tail }
    - strategy_master_promotion_test: { exit_code, duration_seconds, output_tail }
    - strategy_validator_smoke_test: { exit_code, duration_seconds, output_tail }
    - brawler_orchestrator_test: { exit_code, duration_seconds, output_tail }
    - brawler_registry_test: { exit_code, duration_seconds, output_tail }
    - brawler_contracts_test: { exit_code, duration_seconds, output_tail }
    - brawler_master_promotion_test: { exit_code, duration_seconds, output_tail }
    - brawler_validator_smoke_test: { exit_code, duration_seconds, output_tail }
    - platformer_orchestrator_test: { exit_code, duration_seconds, output_tail }
    - platformer_registry_test: { exit_code, duration_seconds, output_tail }
    - platformer_contracts_test: { exit_code, duration_seconds, output_tail }
    - platformer_master_promotion_test: { exit_code, duration_seconds, output_tail }
    - platformer_validator_smoke_test: { exit_code, duration_seconds, output_tail }
    - racing_orchestrator_test: { exit_code, duration_seconds, output_tail }
    - racing_registry_test: { exit_code, duration_seconds, output_tail }
    - racing_contracts_test: { exit_code, duration_seconds, output_tail }
    - racing_master_promotion_test: { exit_code, duration_seconds, output_tail }
    - racing_validator_smoke_test: { exit_code, duration_seconds, output_tail }
    - combined_status: passed|failed
    - run_timestamp

.PARAMETER Mode
    full     (default): roda auditor, schemas e metodologia; falha se qualquer um falhar.
    schema:              roda so schemas.
    audit:               roda so auditor.
    smoke:               roda auditor, schemas e metodologia para CI smoke.

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File `
        tools/sgdk_wrapper/ci/run_all_contract_gates.ps1 -Mode full

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File `
        tools/sgdk_wrapper/ci/run_all_contract_gates.ps1 -Mode smoke

.EXIT_CODES
    0 = todos os gates passaram
    1 = algum gate falhou
    2 = erro de infra (script ausente, etc)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("full", "schema", "audit", "smoke")]
    [string]$Mode = "full",

    [Parameter(Mandatory = $false)]
    [string]$OutputDir = ""
)

$ErrorActionPreference = 'Stop'

$ciDir = $PSScriptRoot
$wrapperRoot = Split-Path $ciDir -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $workspaceRoot "out\ci"
}
if (-not (Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
}

$reportPath = Join-Path $OutputDir "contract_gates_report.json"

$agentStartupScript = Join-Path $ciDir "test_agent_startup_environment.ps1"
$auditScript = Join-Path $ciDir "test_game_design_contract_gates.ps1"
$schemaScript = Join-Path $ciDir "test_schema_contract_gates.py"
$artGameplayDirectionGateScript = Join-Path $ciDir "test_art_gameplay_direction_gate.ps1"
$projectContextScript = Join-Path $ciDir "test_project_context_governance.ps1"
$methodologyScript = Join-Path $ciDir "test_project_methodology_governance.ps1"
$bootstrapScript = Join-Path $ciDir "test_project_bootstrap_qaproof.ps1"
$vibeTemplateBirthScript = Join-Path $ciDir "test_vibe_playable_template_birth.ps1"
$freshnessScript = Join-Path $ciDir "test_freshness_audit.ps1"
$hygieneScript = Join-Path $ciDir "test_project_hygiene_governance.ps1"
$techniqueUsageScript = Join-Path $ciDir "test_technique_usage_governance.ps1"
$statusSyncScript = Join-Path $ciDir "test_changelog_status_sync.ps1"
$projectLearningScript = Join-Path $ciDir "test_project_learning_loop.py"
$genreRegistryScript = Join-Path $ciDir "test_genre_specialization_registry.ps1"
$fightingOrchestratorScript = Join-Path $ciDir "test_fighting_specialization_orchestrator.ps1"
$fightingContractsScript = Join-Path $ciDir "test_fighting_specialization_contracts.ps1"
$fightingMasterPromotionScript = Join-Path $ciDir "test_fighting_master_promotion_guard.ps1"
$fightingValidatorSmokeScript = Join-Path $ciDir "test_fighting_specialization_validator_smoke.ps1"
$rpgOrchestratorScript = Join-Path $ciDir "test_rpg_specialization_orchestrator.ps1"
$rpgRegistryScript = Join-Path $ciDir "test_rpg_specialization_registry.ps1"
$rpgContractsScript = Join-Path $ciDir "test_rpg_specialization_contracts.ps1"
$rpgMasterPromotionScript = Join-Path $ciDir "test_rpg_master_promotion_guard.ps1"
$rpgValidatorSmokeScript = Join-Path $ciDir "test_rpg_specialization_validator_smoke.ps1"
$strategyOrchestratorScript = Join-Path $ciDir "test_strategy_specialization_orchestrator.ps1"
$strategyRegistryScript = Join-Path $ciDir "test_strategy_specialization_registry.ps1"
$strategyContractsScript = Join-Path $ciDir "test_strategy_specialization_contracts.ps1"
$strategyMasterPromotionScript = Join-Path $ciDir "test_strategy_master_promotion_guard.ps1"
$strategyValidatorSmokeScript = Join-Path $ciDir "test_strategy_specialization_validator_smoke.ps1"
$brawlerOrchestratorScript = Join-Path $ciDir "test_brawler_specialization_orchestrator.ps1"
$brawlerRegistryScript = Join-Path $ciDir "test_brawler_specialization_registry.ps1"
$brawlerContractsScript = Join-Path $ciDir "test_brawler_specialization_contracts.ps1"
$brawlerMasterPromotionScript = Join-Path $ciDir "test_brawler_master_promotion_guard.ps1"
$brawlerValidatorSmokeScript = Join-Path $ciDir "test_brawler_specialization_validator_smoke.ps1"
$platformerOrchestratorScript = Join-Path $ciDir "test_platformer_specialization_orchestrator.ps1"
$platformerRegistryScript = Join-Path $ciDir "test_platformer_specialization_registry.ps1"
$platformerContractsScript = Join-Path $ciDir "test_platformer_specialization_contracts.ps1"
$platformerMasterPromotionScript = Join-Path $ciDir "test_platformer_master_promotion_guard.ps1"
$platformerValidatorSmokeScript = Join-Path $ciDir "test_platformer_specialization_validator_smoke.ps1"
$racingOrchestratorScript = Join-Path $ciDir "test_racing_specialization_orchestrator.ps1"
$racingRegistryScript = Join-Path $ciDir "test_racing_specialization_registry.ps1"
$racingContractsScript = Join-Path $ciDir "test_racing_specialization_contracts.ps1"
$racingMasterPromotionScript = Join-Path $ciDir "test_racing_master_promotion_guard.ps1"
$racingValidatorSmokeScript = Join-Path $ciDir "test_racing_specialization_validator_smoke.ps1"
$pythonExe = "uv"
$pythonPrefixArgs = @("run", "--with", "jsonschema", "python")

$runTimestamp = (Get-Date).ToString("o")
$report = [ordered]@{
    schema_version = "1.0.0"
    run_id = "contract_gates_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    run_timestamp = $runTimestamp
    mode = $Mode
    workspace_root = $workspaceRoot
    wrapper_root = $wrapperRoot
    agent_startup_test = $null
    audit_test = $null
    schema_test = $null
    art_gameplay_direction_gate_test = $null
    project_context_test = $null
    methodology_test = $null
    bootstrap_test = $null
    vibe_template_birth_test = $null
    freshness_test = $null
    hygiene_test = $null
    technique_usage_test = $null
    status_sync_test = $null
    project_learning_test = $null
    genre_registry_test = $null
    fighting_orchestrator_test = $null
    fighting_contracts_test = $null
    fighting_master_promotion_test = $null
    fighting_validator_smoke_test = $null
    rpg_orchestrator_test = $null
    rpg_registry_test = $null
    rpg_contracts_test = $null
    rpg_master_promotion_test = $null
    rpg_validator_smoke_test = $null
    strategy_orchestrator_test = $null
    strategy_registry_test = $null
    strategy_contracts_test = $null
    strategy_master_promotion_test = $null
    strategy_validator_smoke_test = $null
    brawler_orchestrator_test = $null
    brawler_registry_test = $null
    brawler_contracts_test = $null
    brawler_master_promotion_test = $null
    brawler_validator_smoke_test = $null
    platformer_orchestrator_test = $null
    platformer_registry_test = $null
    platformer_contracts_test = $null
    platformer_master_promotion_test = $null
    platformer_validator_smoke_test = $null
    racing_orchestrator_test = $null
    racing_registry_test = $null
    racing_contracts_test = $null
    racing_master_promotion_test = $null
    racing_validator_smoke_test = $null
    combined_status = "unknown"
}

function Run-Step {
    param(
        [string]$Name,
        [string]$Command,
        [string[]]$CommandArgs
    )
    Write-Host ""
    Write-Host "=== $Name ==="
    $startTime = Get-Date
    $output = ""
    $exitCode = 0
    try {
        if ($CommandArgs.Count -gt 0) {
            $output = & $Command @CommandArgs 2>&1 | Out-String
        } else {
            $output = & $Command 2>&1 | Out-String
        }
        $exitCode = $LASTEXITCODE
    } catch {
        $output = $_.Exception.Message
        $exitCode = 2
    }
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    Write-Host $output
    Write-Host "  exit_code=$exitCode duration=${duration}s"
    return @{
        exit_code = $exitCode
        duration_seconds = [math]::Round($duration, 2)
        output_tail = ($output -split "`n" | Select-Object -Last 5) -join "`n"
    }
}

$agentStartupRan = $false
$auditRan = $false
$schemaRan = $false
$artGameplayDirectionGateRan = $false
$projectContextRan = $false
$methodologyRan = $false
$bootstrapRan = $false
$vibeTemplateBirthRan = $false
$freshnessRan = $false
$hygieneRan = $false
$techniqueUsageRan = $false
$statusSyncRan = $false
$projectLearningRan = $false
$genreRegistryRan = $false
$fightingOrchestratorRan = $false
$fightingContractsRan = $false
$fightingMasterPromotionRan = $false
$fightingValidatorSmokeRan = $false
$rpgOrchestratorRan = $false
$rpgRegistryRan = $false
$rpgContractsRan = $false
$rpgMasterPromotionRan = $false
$rpgValidatorSmokeRan = $false
$strategyOrchestratorRan = $false
$strategyRegistryRan = $false
$strategyContractsRan = $false
$strategyMasterPromotionRan = $false
$strategyValidatorSmokeRan = $false
$brawlerOrchestratorRan = $false
$brawlerRegistryRan = $false
$brawlerContractsRan = $false
$brawlerMasterPromotionRan = $false
$brawlerValidatorSmokeRan = $false
$platformerOrchestratorRan = $false
$platformerRegistryRan = $false
$platformerContractsRan = $false
$platformerMasterPromotionRan = $false
$platformerValidatorSmokeRan = $false
$racingOrchestratorRan = $false
$racingRegistryRan = $false
$racingContractsRan = $false
$racingMasterPromotionRan = $false
$racingValidatorSmokeRan = $false

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $agentStartupScript)) {
        Write-Host "[ERROR] agent startup test not found: $agentStartupScript"
        $report.agent_startup_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "agent_startup_environment (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $agentStartupScript)
        $report.agent_startup_test = $result
        $agentStartupRan = $true
    }
}

if ($Mode -in @("full", "audit", "smoke")) {
    if (-not (Test-Path -LiteralPath $auditScript)) {
        Write-Host "[ERROR] audit test not found: $auditScript"
        $report.audit_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "audit_game_design_contracts (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $auditScript)
        $report.audit_test = $result
        $auditRan = $true
    }
}

if ($Mode -in @("full", "schema", "smoke")) {
    if (-not (Test-Path -LiteralPath $schemaScript)) {
        Write-Host "[ERROR] schema test not found: $schemaScript"
        $report.schema_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "schema_contract_gates (Python jsonschema)" -Command $pythonExe -CommandArgs ($pythonPrefixArgs + @($schemaScript))
        $report.schema_test = $result
        $schemaRan = $true
    }
}

if ($Mode -in @("full", "schema", "smoke")) {
    if (-not (Test-Path -LiteralPath $artGameplayDirectionGateScript)) {
        Write-Host "[ERROR] art gameplay direction gate test not found: $artGameplayDirectionGateScript"
        $report.art_gameplay_direction_gate_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "art_gameplay_direction_gate (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $artGameplayDirectionGateScript)
        $report.art_gameplay_direction_gate_test = $result
        $artGameplayDirectionGateRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $projectContextScript)) {
        Write-Host "[ERROR] project context test not found: $projectContextScript"
        $report.project_context_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "project_context_governance (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $projectContextScript)
        $report.project_context_test = $result
        $projectContextRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $methodologyScript)) {
        Write-Host "[ERROR] methodology test not found: $methodologyScript"
        $report.methodology_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "project_methodology_governance (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $methodologyScript)
        $report.methodology_test = $result
        $methodologyRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $techniqueUsageScript)) {
        Write-Host "[ERROR] technique usage test not found: $techniqueUsageScript"
        $report.technique_usage_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "technique_usage_governance (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $techniqueUsageScript)
        $report.technique_usage_test = $result
        $techniqueUsageRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $hygieneScript)) {
        Write-Host "[ERROR] hygiene test not found: $hygieneScript"
        $report.hygiene_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "project_hygiene_governance (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $hygieneScript)
        $report.hygiene_test = $result
        $hygieneRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $freshnessScript)) {
        Write-Host "[ERROR] freshness test not found: $freshnessScript"
        $report.freshness_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "freshness_audit_propagation (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $freshnessScript)
        $report.freshness_test = $result
        $freshnessRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $bootstrapScript)) {
        Write-Host "[ERROR] bootstrap test not found: $bootstrapScript"
        $report.bootstrap_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "project_bootstrap_qaproof (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $bootstrapScript)
        $report.bootstrap_test = $result
        $bootstrapRan = $true
    }
}
if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $vibeTemplateBirthScript)) {
        Write-Host "[ERROR] vibe template birth test not found: $vibeTemplateBirthScript"
        $report.vibe_template_birth_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "vibe_playable_template_birth (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $vibeTemplateBirthScript)
        $report.vibe_template_birth_test = $result
        $vibeTemplateBirthRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $statusSyncScript)) {
        Write-Host "[ERROR] status sync test not found: $statusSyncScript"
        $report.status_sync_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "changelog_status_sync (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $statusSyncScript)
        $report.status_sync_test = $result
        $statusSyncRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $projectLearningScript)) {
        Write-Host "[ERROR] project learning test not found: $projectLearningScript"
        $report.project_learning_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "project_learning_loop (Python)" -Command $pythonExe -CommandArgs ($pythonPrefixArgs + @($projectLearningScript))
        $report.project_learning_test = $result
        $projectLearningRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $genreRegistryScript)) {
        Write-Host "[ERROR] genre registry test not found: $genreRegistryScript"
        $report.genre_registry_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "genre_specialization_registry (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $genreRegistryScript)
        $report.genre_registry_test = $result
        $genreRegistryRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $fightingOrchestratorScript)) {
        Write-Host "[ERROR] fighting orchestrator test not found: $fightingOrchestratorScript"
        $report.fighting_orchestrator_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "fighting_specialization_orchestrator (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $fightingOrchestratorScript)
        $report.fighting_orchestrator_test = $result
        $fightingOrchestratorRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $fightingContractsScript)) {
        Write-Host "[ERROR] fighting contracts test not found: $fightingContractsScript"
        $report.fighting_contracts_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "fighting_specialization_contracts (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $fightingContractsScript)
        $report.fighting_contracts_test = $result
        $fightingContractsRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $fightingMasterPromotionScript)) {
        Write-Host "[ERROR] fighting master promotion test not found: $fightingMasterPromotionScript"
        $report.fighting_master_promotion_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "fighting_master_promotion_guard (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $fightingMasterPromotionScript)
        $report.fighting_master_promotion_test = $result
        $fightingMasterPromotionRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $fightingValidatorSmokeScript)) {
        Write-Host "[ERROR] fighting validator smoke test not found: $fightingValidatorSmokeScript"
        $report.fighting_validator_smoke_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "fighting_specialization_validator_smoke (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $fightingValidatorSmokeScript)
        $report.fighting_validator_smoke_test = $result
        $fightingValidatorSmokeRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $rpgOrchestratorScript)) {
        Write-Host "[ERROR] rpg orchestrator test not found: $rpgOrchestratorScript"
        $report.rpg_orchestrator_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "rpg_specialization_orchestrator (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $rpgOrchestratorScript)
        $report.rpg_orchestrator_test = $result
        $rpgOrchestratorRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $rpgRegistryScript)) {
        Write-Host "[ERROR] rpg registry test not found: $rpgRegistryScript"
        $report.rpg_registry_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "rpg_specialization_registry (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $rpgRegistryScript)
        $report.rpg_registry_test = $result
        $rpgRegistryRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $rpgContractsScript)) {
        Write-Host "[ERROR] rpg contracts test not found: $rpgContractsScript"
        $report.rpg_contracts_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "rpg_specialization_contracts (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $rpgContractsScript)
        $report.rpg_contracts_test = $result
        $rpgContractsRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $rpgMasterPromotionScript)) {
        Write-Host "[ERROR] rpg master promotion test not found: $rpgMasterPromotionScript"
        $report.rpg_master_promotion_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "rpg_master_promotion_guard (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $rpgMasterPromotionScript)
        $report.rpg_master_promotion_test = $result
        $rpgMasterPromotionRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $rpgValidatorSmokeScript)) {
        Write-Host "[ERROR] rpg validator smoke test not found: $rpgValidatorSmokeScript"
        $report.rpg_validator_smoke_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "rpg_specialization_validator_smoke (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $rpgValidatorSmokeScript)
        $report.rpg_validator_smoke_test = $result
        $rpgValidatorSmokeRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $strategyOrchestratorScript)) {
        Write-Host "[ERROR] strategy orchestrator test not found: $strategyOrchestratorScript"
        $report.strategy_orchestrator_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "strategy_specialization_orchestrator (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $strategyOrchestratorScript)
        $report.strategy_orchestrator_test = $result
        $strategyOrchestratorRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $strategyRegistryScript)) {
        Write-Host "[ERROR] strategy registry test not found: $strategyRegistryScript"
        $report.strategy_registry_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "strategy_specialization_registry (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $strategyRegistryScript)
        $report.strategy_registry_test = $result
        $strategyRegistryRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $strategyContractsScript)) {
        Write-Host "[ERROR] strategy contracts test not found: $strategyContractsScript"
        $report.strategy_contracts_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "strategy_specialization_contracts (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $strategyContractsScript)
        $report.strategy_contracts_test = $result
        $strategyContractsRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $strategyMasterPromotionScript)) {
        Write-Host "[ERROR] strategy master promotion test not found: $strategyMasterPromotionScript"
        $report.strategy_master_promotion_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "strategy_master_promotion_guard (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $strategyMasterPromotionScript)
        $report.strategy_master_promotion_test = $result
        $strategyMasterPromotionRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $strategyValidatorSmokeScript)) {
        Write-Host "[ERROR] strategy validator smoke test not found: $strategyValidatorSmokeScript"
        $report.strategy_validator_smoke_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "strategy_specialization_validator_smoke (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $strategyValidatorSmokeScript)
        $report.strategy_validator_smoke_test = $result
        $strategyValidatorSmokeRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $brawlerOrchestratorScript)) {
        Write-Host "[ERROR] brawler orchestrator test not found: $brawlerOrchestratorScript"
        $report.brawler_orchestrator_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "brawler_specialization_orchestrator (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $brawlerOrchestratorScript)
        $report.brawler_orchestrator_test = $result
        $brawlerOrchestratorRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $brawlerRegistryScript)) {
        Write-Host "[ERROR] brawler registry test not found: $brawlerRegistryScript"
        $report.brawler_registry_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "brawler_specialization_registry (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $brawlerRegistryScript)
        $report.brawler_registry_test = $result
        $brawlerRegistryRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $brawlerContractsScript)) {
        Write-Host "[ERROR] brawler contracts test not found: $brawlerContractsScript"
        $report.brawler_contracts_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "brawler_specialization_contracts (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $brawlerContractsScript)
        $report.brawler_contracts_test = $result
        $brawlerContractsRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $brawlerMasterPromotionScript)) {
        Write-Host "[ERROR] brawler master promotion test not found: $brawlerMasterPromotionScript"
        $report.brawler_master_promotion_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "brawler_master_promotion_guard (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $brawlerMasterPromotionScript)
        $report.brawler_master_promotion_test = $result
        $brawlerMasterPromotionRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $brawlerValidatorSmokeScript)) {
        Write-Host "[ERROR] brawler validator smoke test not found: $brawlerValidatorSmokeScript"
        $report.brawler_validator_smoke_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "brawler_specialization_validator_smoke (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $brawlerValidatorSmokeScript)
        $report.brawler_validator_smoke_test = $result
        $brawlerValidatorSmokeRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $platformerOrchestratorScript)) {
        Write-Host "[ERROR] platformer orchestrator test not found: $platformerOrchestratorScript"
        $report.platformer_orchestrator_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "platformer_specialization_orchestrator (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $platformerOrchestratorScript)
        $report.platformer_orchestrator_test = $result
        $platformerOrchestratorRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $platformerRegistryScript)) {
        Write-Host "[ERROR] platformer registry test not found: $platformerRegistryScript"
        $report.platformer_registry_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "platformer_specialization_registry (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $platformerRegistryScript)
        $report.platformer_registry_test = $result
        $platformerRegistryRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $platformerContractsScript)) {
        Write-Host "[ERROR] platformer contracts test not found: $platformerContractsScript"
        $report.platformer_contracts_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "platformer_specialization_contracts (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $platformerContractsScript)
        $report.platformer_contracts_test = $result
        $platformerContractsRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $platformerMasterPromotionScript)) {
        Write-Host "[ERROR] platformer master promotion test not found: $platformerMasterPromotionScript"
        $report.platformer_master_promotion_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "platformer_master_promotion_guard (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $platformerMasterPromotionScript)
        $report.platformer_master_promotion_test = $result
        $platformerMasterPromotionRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $platformerValidatorSmokeScript)) {
        Write-Host "[ERROR] platformer validator smoke test not found: $platformerValidatorSmokeScript"
        $report.platformer_validator_smoke_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "platformer_specialization_validator_smoke (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $platformerValidatorSmokeScript)
        $report.platformer_validator_smoke_test = $result
        $platformerValidatorSmokeRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $racingOrchestratorScript)) {
        Write-Host "[ERROR] racing orchestrator test not found: $racingOrchestratorScript"
        $report.racing_orchestrator_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "racing_specialization_orchestrator (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $racingOrchestratorScript)
        $report.racing_orchestrator_test = $result
        $racingOrchestratorRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $racingRegistryScript)) {
        Write-Host "[ERROR] racing registry test not found: $racingRegistryScript"
        $report.racing_registry_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "racing_specialization_registry (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $racingRegistryScript)
        $report.racing_registry_test = $result
        $racingRegistryRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $racingContractsScript)) {
        Write-Host "[ERROR] racing contracts test not found: $racingContractsScript"
        $report.racing_contracts_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "racing_specialization_contracts (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $racingContractsScript)
        $report.racing_contracts_test = $result
        $racingContractsRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $racingMasterPromotionScript)) {
        Write-Host "[ERROR] racing master promotion test not found: $racingMasterPromotionScript"
        $report.racing_master_promotion_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "racing_master_promotion_guard (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $racingMasterPromotionScript)
        $report.racing_master_promotion_test = $result
        $racingMasterPromotionRan = $true
    }
}

if ($Mode -in @("full", "smoke")) {
    if (-not (Test-Path -LiteralPath $racingValidatorSmokeScript)) {
        Write-Host "[ERROR] racing validator smoke test not found: $racingValidatorSmokeScript"
        $report.racing_validator_smoke_test = @{ exit_code = 2; duration_seconds = 0; error = "script not found" }
    } else {
        $result = Run-Step -Name "racing_specialization_validator_smoke (PowerShell)" -Command "powershell.exe" -CommandArgs @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $racingValidatorSmokeScript)
        $report.racing_validator_smoke_test = $result
        $racingValidatorSmokeRan = $true
    }
}

# Determina status combinado
$combinedExit = 0
if ($agentStartupRan -and $report.agent_startup_test.exit_code -ne 0) { $combinedExit = 1 }
if ($auditRan -and $report.audit_test.exit_code -ne 0) { $combinedExit = 1 }
if ($schemaRan -and $report.schema_test.exit_code -ne 0) { $combinedExit = 1 }
if ($artGameplayDirectionGateRan -and $report.art_gameplay_direction_gate_test.exit_code -ne 0) { $combinedExit = 1 }
if ($projectContextRan -and $report.project_context_test.exit_code -ne 0) { $combinedExit = 1 }
if ($methodologyRan -and $report.methodology_test.exit_code -ne 0) { $combinedExit = 1 }
if ($bootstrapRan -and $report.bootstrap_test.exit_code -ne 0) { $combinedExit = 1 }
if ($vibeTemplateBirthRan -and $report.vibe_template_birth_test.exit_code -ne 0) { $combinedExit = 1 }
if ($freshnessRan -and $report.freshness_test.exit_code -ne 0) { $combinedExit = 1 }
if ($hygieneRan -and $report.hygiene_test.exit_code -ne 0) { $combinedExit = 1 }
if ($techniqueUsageRan -and $report.technique_usage_test.exit_code -ne 0) { $combinedExit = 1 }
if ($statusSyncRan -and $report.status_sync_test.exit_code -ne 0) { $combinedExit = 1 }
if ($projectLearningRan -and $report.project_learning_test.exit_code -ne 0) { $combinedExit = 1 }
if ($genreRegistryRan -and $report.genre_registry_test.exit_code -ne 0) { $combinedExit = 1 }
if ($fightingOrchestratorRan -and $report.fighting_orchestrator_test.exit_code -ne 0) { $combinedExit = 1 }
if ($fightingContractsRan -and $report.fighting_contracts_test.exit_code -ne 0) { $combinedExit = 1 }
if ($fightingMasterPromotionRan -and $report.fighting_master_promotion_test.exit_code -ne 0) { $combinedExit = 1 }
if ($fightingValidatorSmokeRan -and $report.fighting_validator_smoke_test.exit_code -ne 0) { $combinedExit = 1 }
if ($rpgOrchestratorRan -and $report.rpg_orchestrator_test.exit_code -ne 0) { $combinedExit = 1 }
if ($rpgRegistryRan -and $report.rpg_registry_test.exit_code -ne 0) { $combinedExit = 1 }
if ($rpgContractsRan -and $report.rpg_contracts_test.exit_code -ne 0) { $combinedExit = 1 }
if ($rpgMasterPromotionRan -and $report.rpg_master_promotion_test.exit_code -ne 0) { $combinedExit = 1 }
if ($rpgValidatorSmokeRan -and $report.rpg_validator_smoke_test.exit_code -ne 0) { $combinedExit = 1 }
if ($strategyOrchestratorRan -and $report.strategy_orchestrator_test.exit_code -ne 0) { $combinedExit = 1 }
if ($strategyRegistryRan -and $report.strategy_registry_test.exit_code -ne 0) { $combinedExit = 1 }
if ($strategyContractsRan -and $report.strategy_contracts_test.exit_code -ne 0) { $combinedExit = 1 }
if ($strategyMasterPromotionRan -and $report.strategy_master_promotion_test.exit_code -ne 0) { $combinedExit = 1 }
if ($strategyValidatorSmokeRan -and $report.strategy_validator_smoke_test.exit_code -ne 0) { $combinedExit = 1 }
if ($brawlerOrchestratorRan -and $report.brawler_orchestrator_test.exit_code -ne 0) { $combinedExit = 1 }
if ($brawlerRegistryRan -and $report.brawler_registry_test.exit_code -ne 0) { $combinedExit = 1 }
if ($brawlerContractsRan -and $report.brawler_contracts_test.exit_code -ne 0) { $combinedExit = 1 }
if ($brawlerMasterPromotionRan -and $report.brawler_master_promotion_test.exit_code -ne 0) { $combinedExit = 1 }
if ($brawlerValidatorSmokeRan -and $report.brawler_validator_smoke_test.exit_code -ne 0) { $combinedExit = 1 }
if ($platformerOrchestratorRan -and $report.platformer_orchestrator_test.exit_code -ne 0) { $combinedExit = 1 }
if ($platformerRegistryRan -and $report.platformer_registry_test.exit_code -ne 0) { $combinedExit = 1 }
if ($platformerContractsRan -and $report.platformer_contracts_test.exit_code -ne 0) { $combinedExit = 1 }
if ($platformerMasterPromotionRan -and $report.platformer_master_promotion_test.exit_code -ne 0) { $combinedExit = 1 }
if ($platformerValidatorSmokeRan -and $report.platformer_validator_smoke_test.exit_code -ne 0) { $combinedExit = 1 }
if ($racingOrchestratorRan -and $report.racing_orchestrator_test.exit_code -ne 0) { $combinedExit = 1 }
if ($racingRegistryRan -and $report.racing_registry_test.exit_code -ne 0) { $combinedExit = 1 }
if ($racingContractsRan -and $report.racing_contracts_test.exit_code -ne 0) { $combinedExit = 1 }
if ($racingMasterPromotionRan -and $report.racing_master_promotion_test.exit_code -ne 0) { $combinedExit = 1 }
if ($racingValidatorSmokeRan -and $report.racing_validator_smoke_test.exit_code -ne 0) { $combinedExit = 1 }

$report.combined_status = if ($combinedExit -eq 0) { "passed" } else { "failed" }
$report.combined_exit_code = $combinedExit

$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8

Write-Host ""
Write-Host "=== Resumo ==="
Write-Host "agent_startup_test exit_code: $(if ($null -eq $report.agent_startup_test) { 'not_run' } else { $report.agent_startup_test.exit_code })"
Write-Host "audit_test exit_code: $(if ($null -eq $report.audit_test) { 'not_run' } else { $report.audit_test.exit_code })"
Write-Host "schema_test exit_code: $(if ($null -eq $report.schema_test) { 'not_run' } else { $report.schema_test.exit_code })"
Write-Host "art_gameplay_direction_gate_test exit_code: $(if ($null -eq $report.art_gameplay_direction_gate_test) { 'not_run' } else { $report.art_gameplay_direction_gate_test.exit_code })"
Write-Host "project_context_test exit_code: $(if ($null -eq $report.project_context_test) { 'not_run' } else { $report.project_context_test.exit_code })"
Write-Host "methodology_test exit_code: $(if ($null -eq $report.methodology_test) { 'not_run' } else { $report.methodology_test.exit_code })"
Write-Host "bootstrap_test exit_code: $(if ($null -eq $report.bootstrap_test) { 'not_run' } else { $report.bootstrap_test.exit_code })"
Write-Host "vibe_template_birth_test exit_code: $(if ($null -eq $report.vibe_template_birth_test) { 'not_run' } else { $report.vibe_template_birth_test.exit_code })"
Write-Host "freshness_test exit_code: $(if ($null -eq $report.freshness_test) { 'not_run' } else { $report.freshness_test.exit_code })"
Write-Host "hygiene_test exit_code: $(if ($null -eq $report.hygiene_test) { 'not_run' } else { $report.hygiene_test.exit_code })"
Write-Host "technique_usage_test exit_code: $(if ($null -eq $report.technique_usage_test) { 'not_run' } else { $report.technique_usage_test.exit_code })"
Write-Host "status_sync_test exit_code: $(if ($null -eq $report.status_sync_test) { 'not_run' } else { $report.status_sync_test.exit_code })"
Write-Host "project_learning_test exit_code: $(if ($null -eq $report.project_learning_test) { 'not_run' } else { $report.project_learning_test.exit_code })"
Write-Host "genre_registry_test exit_code: $(if ($null -eq $report.genre_registry_test) { 'not_run' } else { $report.genre_registry_test.exit_code })"
Write-Host "fighting_orchestrator_test exit_code: $(if ($null -eq $report.fighting_orchestrator_test) { 'not_run' } else { $report.fighting_orchestrator_test.exit_code })"
Write-Host "fighting_contracts_test exit_code: $(if ($null -eq $report.fighting_contracts_test) { 'not_run' } else { $report.fighting_contracts_test.exit_code })"
Write-Host "fighting_master_promotion_test exit_code: $(if ($null -eq $report.fighting_master_promotion_test) { 'not_run' } else { $report.fighting_master_promotion_test.exit_code })"
Write-Host "fighting_validator_smoke_test exit_code: $(if ($null -eq $report.fighting_validator_smoke_test) { 'not_run' } else { $report.fighting_validator_smoke_test.exit_code })"
Write-Host "rpg_orchestrator_test exit_code: $(if ($null -eq $report.rpg_orchestrator_test) { 'not_run' } else { $report.rpg_orchestrator_test.exit_code })"
Write-Host "rpg_registry_test exit_code: $(if ($null -eq $report.rpg_registry_test) { 'not_run' } else { $report.rpg_registry_test.exit_code })"
Write-Host "rpg_contracts_test exit_code: $(if ($null -eq $report.rpg_contracts_test) { 'not_run' } else { $report.rpg_contracts_test.exit_code })"
Write-Host "rpg_master_promotion_test exit_code: $(if ($null -eq $report.rpg_master_promotion_test) { 'not_run' } else { $report.rpg_master_promotion_test.exit_code })"
Write-Host "rpg_validator_smoke_test exit_code: $(if ($null -eq $report.rpg_validator_smoke_test) { 'not_run' } else { $report.rpg_validator_smoke_test.exit_code })"
Write-Host "strategy_orchestrator_test exit_code: $(if ($null -eq $report.strategy_orchestrator_test) { 'not_run' } else { $report.strategy_orchestrator_test.exit_code })"
Write-Host "strategy_registry_test exit_code: $(if ($null -eq $report.strategy_registry_test) { 'not_run' } else { $report.strategy_registry_test.exit_code })"
Write-Host "strategy_contracts_test exit_code: $(if ($null -eq $report.strategy_contracts_test) { 'not_run' } else { $report.strategy_contracts_test.exit_code })"
Write-Host "strategy_master_promotion_test exit_code: $(if ($null -eq $report.strategy_master_promotion_test) { 'not_run' } else { $report.strategy_master_promotion_test.exit_code })"
Write-Host "strategy_validator_smoke_test exit_code: $(if ($null -eq $report.strategy_validator_smoke_test) { 'not_run' } else { $report.strategy_validator_smoke_test.exit_code })"
Write-Host "brawler_orchestrator_test exit_code: $(if ($null -eq $report.brawler_orchestrator_test) { 'not_run' } else { $report.brawler_orchestrator_test.exit_code })"
Write-Host "brawler_registry_test exit_code: $(if ($null -eq $report.brawler_registry_test) { 'not_run' } else { $report.brawler_registry_test.exit_code })"
Write-Host "brawler_contracts_test exit_code: $(if ($null -eq $report.brawler_contracts_test) { 'not_run' } else { $report.brawler_contracts_test.exit_code })"
Write-Host "brawler_master_promotion_test exit_code: $(if ($null -eq $report.brawler_master_promotion_test) { 'not_run' } else { $report.brawler_master_promotion_test.exit_code })"
Write-Host "brawler_validator_smoke_test exit_code: $(if ($null -eq $report.brawler_validator_smoke_test) { 'not_run' } else { $report.brawler_validator_smoke_test.exit_code })"
Write-Host "platformer_orchestrator_test exit_code: $(if ($null -eq $report.platformer_orchestrator_test) { 'not_run' } else { $report.platformer_orchestrator_test.exit_code })"
Write-Host "platformer_registry_test exit_code: $(if ($null -eq $report.platformer_registry_test) { 'not_run' } else { $report.platformer_registry_test.exit_code })"
Write-Host "platformer_contracts_test exit_code: $(if ($null -eq $report.platformer_contracts_test) { 'not_run' } else { $report.platformer_contracts_test.exit_code })"
Write-Host "platformer_master_promotion_test exit_code: $(if ($null -eq $report.platformer_master_promotion_test) { 'not_run' } else { $report.platformer_master_promotion_test.exit_code })"
Write-Host "platformer_validator_smoke_test exit_code: $(if ($null -eq $report.platformer_validator_smoke_test) { 'not_run' } else { $report.platformer_validator_smoke_test.exit_code })"
Write-Host "racing_orchestrator_test exit_code: $(if ($null -eq $report.racing_orchestrator_test) { 'not_run' } else { $report.racing_orchestrator_test.exit_code })"
Write-Host "racing_registry_test exit_code: $(if ($null -eq $report.racing_registry_test) { 'not_run' } else { $report.racing_registry_test.exit_code })"
Write-Host "racing_contracts_test exit_code: $(if ($null -eq $report.racing_contracts_test) { 'not_run' } else { $report.racing_contracts_test.exit_code })"
Write-Host "racing_master_promotion_test exit_code: $(if ($null -eq $report.racing_master_promotion_test) { 'not_run' } else { $report.racing_master_promotion_test.exit_code })"
Write-Host "racing_validator_smoke_test exit_code: $(if ($null -eq $report.racing_validator_smoke_test) { 'not_run' } else { $report.racing_validator_smoke_test.exit_code })"
Write-Host "combined_status: $($report.combined_status)"
Write-Host "report: $reportPath"

if ($combinedExit -ne 0) { exit 1 }
exit 0
