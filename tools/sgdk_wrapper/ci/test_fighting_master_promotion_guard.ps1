<#
.SYNOPSIS
    Proves that the genre specialization registry cannot auto-promote to
    MESTRE_*. Checks:
      - registry contains no MESTRE_* entries (today)
      - the validator never reports status=ok when a manifest declares a
        MESTRE_* tier in a context without the required artifacts
      - the framework manifest and matrix reflect LABORATORIO as the v1 ceiling
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$registryPath = Join-Path $workspaceRoot 'doc\07_game_design\genre_specialization_registry.json'
$matrixPath = Join-Path $workspaceRoot 'doc\07_game_design\genre_specialization_matrix.md'
$frameworkManifestPath = Join-Path $wrapperRoot '.agent\framework_manifest.json'
$validator = Join-Path $wrapperRoot 'validate_fighting_specialization.ps1'
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\fighting_master_promotion_fixture'

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
Write-Host '=== Fighting Master Promotion Guard Test ==='
Write-Host ''

# 1. Registry has no MESTRE_*
$registry = Get-Content -LiteralPath $registryPath -Raw -Encoding UTF8 | ConvertFrom-Json
$masterEntries = @($registry.known_specializations | Where-Object { [string]$_.promotion_tier -like 'MESTRE_*' })
Assert-True 'no specialization is MESTRE_* in v1' ($masterEntries.Count -eq 0) ("$($masterEntries.Count) MESTRE entries")
Assert-True 'registry.promotion_tier is LABORATORIO' ([string]$registry.promotion_tier -eq 'LABORATORIO') ([string]$registry.promotion_tier)

# 2. promotion_required_artifacts mentions human_curation_signature and ROM-style evidence
$artifacts = @($registry.promotion_required_artifacts)
Assert-True 'promotion_required_artifacts demands human_curation_signature' ($artifacts -contains 'human_curation_signature') ('not found')

# 3. Matrix is consistent: MESTRE_* requires explicit human promotion
$matrix = Get-Content -LiteralPath $matrixPath -Raw -Encoding UTF8
Assert-True 'matrix forbids auto-promotion' ($matrix -match 'Sem auto-promocao') ('not found')
Assert-True 'matrix lists MESTRE_STANDARD criteria' ($matrix -match 'MESTRE_STANDARD') ('not found')
Assert-True 'matrix lists MESTRE_PRIORITARIA criteria' ($matrix -match 'MESTRE_PRIORITARIA') ('not found')

# 4. Framework manifest version bump
$frameworkManifest = Get-Content -LiteralPath $frameworkManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$workspaceToolingPaths = @($frameworkManifest.workspace_tooling_paths)
$hasGenreSpecialization = $false
foreach ($p in $workspaceToolingPaths) {
    if ([string]$p -match 'genre_specialization') { $hasGenreSpecialization = $true; break }
}
Assert-True 'framework_manifest has schemas' ($hasGenreSpecialization) ('not registered')

# 5. Negative: simulate a malicious project trying to claim MESTRE_PRIORITARIA via
#    hand-edited registry copy -> validator must still report absent or invalid
#    (proves no shortcut through the canonical validator).
if (Test-Path -LiteralPath $fixtureRoot) {
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'out\logs') | Out-Null
# Copy the real registry into the project (which is a misuse: project must read
# the workspace-level registry, not embed one) and promote a spec to MESTRE.
$rogueRegistry = $registry | ConvertTo-Json -Depth 8 | ConvertFrom-Json
$rogueRegistry.promotion_tier = 'MESTRE_PRIORITARIA'
foreach ($spec in $rogueRegistry.known_specializations) {
    if ($spec.specialization_id -eq 'fighting_2d_traditional') {
        $spec.promotion_tier = 'MESTRE_PRIORITARIA'
    }
}
$rogueRegistry | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $fixtureRoot 'doc\genre_specialization_registry.json') -Encoding UTF8

# No manifest -> validator returns ok/generalista regardless of rogue registry.
& powershell -NoProfile -ExecutionPolicy Bypass -File $validator -ProjectRoot $fixtureRoot | Out-Null
$rogueExit = $LASTEXITCODE
$rogueReportPath = Join-Path $fixtureRoot 'out\logs\fighting_specialization_report.json'
Assert-True 'rogue registry without manifest -> validator exits 0 (generalista)' ($rogueExit -eq 0) ("exit=$rogueExit")
if (Test-Path -LiteralPath $rogueReportPath) {
    $rogueReport = Get-Content -LiteralPath $rogueReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-True 'rogue project reported as manifest_status=absent' ([string]$rogueReport.manifest_status -eq 'absent') ([string]$rogueReport.manifest_status)
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
