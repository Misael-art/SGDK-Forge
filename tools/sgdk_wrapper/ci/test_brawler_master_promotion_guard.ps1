<#
.SYNOPSIS
    Verifies that the brawler_belt_scroll specialization cannot skip
    directly to MESTRE_* without the required artifacts, curation
    signature, and a real validator run.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$registryPath = Join-Path $workspaceRoot 'doc\07_game_design\genre_specialization_registry.json'
$frameworkManifest = Join-Path $wrapperRoot '.agent\framework_manifest.json'
$validator = Join-Path $wrapperRoot 'validate_brawler_belt_scroll_specialization.ps1'

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
Write-Host '=== Brawler Master Promotion Guard Test ==='
Write-Host ''

Assert-True 'registry JSON exists' (Test-Path -LiteralPath $registryPath) $registryPath
Assert-True 'framework_manifest.json exists' (Test-Path -LiteralPath $frameworkManifest) $frameworkManifest
Assert-True 'brawler validator exists' (Test-Path -LiteralPath $validator) $validator

$registry = Get-Content -LiteralPath $registryPath -Raw -Encoding UTF8 | ConvertFrom-Json
$entry = $null
foreach ($k in $registry.known_specializations) {
    if ($k.specialization_id -eq 'brawler_belt_scroll') { $entry = $k; break }
}
Assert-True 'brawler_belt_scroll entry found' ($null -ne $entry) ('not found')

if ($null -ne $entry) {
    Assert-True 'brawler_belt_scroll promotion_tier is LABORATORIO (not MESTRE_*)' ([string]$entry.promotion_tier -eq 'LABORATORIO') ([string]$entry.promotion_tier)
}

Assert-True 'registry has top-level promotion_required_artifacts' ($registry.PSObject.Properties['promotion_required_artifacts'] -and @($registry.promotion_required_artifacts).Count -ge 3) ("$(@($registry.promotion_required_artifacts).Count) artifacts")
Assert-True 'registry has top-level promotion_required_human_roles' ($registry.PSObject.Properties['promotion_required_human_roles'] -and @($registry.promotion_required_human_roles).Count -ge 1) ("$(@($registry.promotion_required_human_roles).Count) roles")
Assert-True 'top-level promotion_required_human_roles contains human_curator' (@($registry.promotion_required_human_roles) -contains 'human_curator') ('not found')

$manifest = Get-Content -LiteralPath $frameworkManifest -Raw -Encoding UTF8 | ConvertFrom-Json
$toolsList = @($manifest.workspace_tooling_paths)
$hasBrawlDesign = $false
$hasBrawlArchetype = $false
$hasBrawlReport = $false
$hasBrawlValidator = $false
foreach ($t in $toolsList) {
    if ([string]$t -match 'brawler_belt_scroll_design_contract') { $hasBrawlDesign = $true }
    if ([string]$t -match 'brawler_enemy_archetype_frame_data') { $hasBrawlArchetype = $true }
    if ([string]$t -match 'brawler_specialization_report') { $hasBrawlReport = $true }
    if ([string]$t -match 'validate_brawler_belt_scroll_specialization\.ps1') { $hasBrawlValidator = $true }
}
Assert-True 'framework_manifest references brawler_belt_scroll_design_contract schema' $hasBrawlDesign ('not in workspace_tooling_paths')
Assert-True 'framework_manifest references brawler_enemy_archetype_frame_data schema' $hasBrawlArchetype ('not in workspace_tooling_paths')
Assert-True 'framework_manifest references brawler_specialization_report schema' $hasBrawlReport ('not in workspace_tooling_paths')
Assert-True 'framework_manifest references validate_brawler_belt_scroll_specialization.ps1' $hasBrawlValidator ('not in workspace_tooling_paths')

$rogueRoot = Join-Path $workspaceRoot 'out\ci\brawler_master_promotion_rogue_fixture'
if (Test-Path -LiteralPath $rogueRoot) { Remove-Item -LiteralPath $rogueRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Join-Path $rogueRoot 'out\logs') | Out-Null
& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $rogueRoot | Out-Null
$rogueExit = $LASTEXITCODE
$rogueReportPath = Join-Path $rogueRoot 'out\logs\brawler_specialization_report.json'
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
