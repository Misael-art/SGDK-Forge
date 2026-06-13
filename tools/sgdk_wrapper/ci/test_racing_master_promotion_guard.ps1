<#
.SYNOPSIS
    Verifies the racing_arcade specialization cannot skip to MESTRE_*.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$registryPath = Join-Path $workspaceRoot 'doc\07_game_design\genre_specialization_registry.json'
$frameworkManifest = Join-Path $wrapperRoot '.agent\framework_manifest.json'
$validator = Join-Path $wrapperRoot 'validate_racing_arcade_specialization.ps1'

$passed = 0
$failed = 0
$total = 0

function Assert-True {
    param([string]$Name, [bool]$Condition, [string]$Detail = '')
    $script:total++
    if ($Condition) {
        $script:passed++
        Write-Host "  [PASS] $Name"
    } else {
        $script:failed++
        $msg = "  [FAIL] $Name"
        if ($Detail) { $msg += " -- $Detail" }
        Write-Host $msg
    }
}

Write-Host ''
Write-Host '=== Racing Master Promotion Guard Test ==='
Write-Host ''

Assert-True 'registry JSON exists' (Test-Path -LiteralPath $registryPath) $registryPath
Assert-True 'framework_manifest.json exists' (Test-Path -LiteralPath $frameworkManifest) $frameworkManifest
Assert-True 'racing validator exists' (Test-Path -LiteralPath $validator) $validator

$registry = Get-Content -LiteralPath $registryPath -Raw -Encoding UTF8 | ConvertFrom-Json
$entry = $null
foreach ($k in $registry.known_specializations) {
    if ($k.specialization_id -eq 'racing_arcade') { $entry = $k; break }
}
Assert-True 'racing_arcade entry found' ($null -ne $entry) ('not found')

if ($null -ne $entry) {
    Assert-True 'racing_arcade promotion_tier is LABORATORIO (not MESTRE_*)' ([string]$entry.promotion_tier -eq 'LABORATORIO') ([string]$entry.promotion_tier)
}

Assert-True 'registry has top-level promotion_required_artifacts' ($registry.PSObject.Properties['promotion_required_artifacts'] -and @($registry.promotion_required_artifacts).Count -ge 3) ("$(@($registry.promotion_required_artifacts).Count) artifacts")
Assert-True 'registry has top-level promotion_required_human_roles' ($registry.PSObject.Properties['promotion_required_human_roles'] -and @($registry.promotion_required_human_roles).Count -ge 1) ("$(@($registry.promotion_required_human_roles).Count) roles")
Assert-True 'top-level promotion_required_human_roles contains human_curator' (@($registry.promotion_required_human_roles) -contains 'human_curator') ('not found')

$manifest = Get-Content -LiteralPath $frameworkManifest -Raw -Encoding UTF8 | ConvertFrom-Json
$toolsList = @($manifest.workspace_tooling_paths)
$hasRaceDesign = $false
$hasRaceVehicle = $false
$hasRaceReport = $false
$hasRaceValidator = $false
foreach ($t in $toolsList) {
    if ([string]$t -match 'racing_arcade_design_contract') { $hasRaceDesign = $true }
    if ([string]$t -match 'racing_vehicle_frame_data') { $hasRaceVehicle = $true }
    if ([string]$t -match 'racing_specialization_report') { $hasRaceReport = $true }
    if ([string]$t -match 'validate_racing_arcade_specialization\.ps1') { $hasRaceValidator = $true }
}
Assert-True 'framework_manifest references racing_arcade_design_contract schema' $hasRaceDesign ('not in workspace_tooling_paths')
Assert-True 'framework_manifest references racing_vehicle_frame_data schema' $hasRaceVehicle ('not in workspace_tooling_paths')
Assert-True 'framework_manifest references racing_specialization_report schema' $hasRaceReport ('not in workspace_tooling_paths')
Assert-True 'framework_manifest references validate_racing_arcade_specialization.ps1' $hasRaceValidator ('not in workspace_tooling_paths')

$rogueRoot = Join-Path $workspaceRoot 'out\ci\racing_master_promotion_rogue_fixture'
if (Test-Path -LiteralPath $rogueRoot) { Remove-Item -LiteralPath $rogueRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $rogueRoot 'out\logs') | Out-Null
& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $rogueRoot | Out-Null
$rogueExit = $LASTEXITCODE
$rogueReportPath = Join-Path $rogueRoot 'out\logs\racing_specialization_report.json'
Assert-True 'rogue registry without manifest -> validator exits 0 (generalista)' ($rogueExit -eq 0) ("exit=$rogueExit")
Assert-True 'rogue project reported as manifest_status=absent' (Test-Path -LiteralPath $rogueReportPath) ('no report')
if (Test-Path -LiteralPath $rogueReportPath) {
    $rogueReport = Get-Content -LiteralPath $rogueReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'rogue report manifest_status is absent' ([string]$rogueReport.manifest_status -eq 'absent') ([string]$rogueReport.manifest_status)
    Assert-True 'rogue report status is ok' ([string]$rogueReport.status -eq 'ok') ([string]$rogueReport.status)
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
