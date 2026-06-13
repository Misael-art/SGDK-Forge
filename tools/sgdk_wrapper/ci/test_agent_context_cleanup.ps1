<#
.SYNOPSIS
    Smoke test seguro do agent_context_cleanup.ps1 em fixture fora do codigo versionado.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$cleanupScript = Join-Path $wrapperRoot 'agent_context_cleanup.ps1'
$canonicalAgent = Join-Path $wrapperRoot '.agent'
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\agent_context_cleanup_scope'
$projectRoot = Join-Path $fixtureRoot 'FixtureProject'
$agentRoot = Join-Path $projectRoot '.agent'
$outputRoot = Join-Path $workspaceRoot 'out\ci\agent_context_cleanup_runs'

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
Write-Host '=== Agent Context Cleanup Test ==='
Write-Host ''

if (Test-Path -LiteralPath $fixtureRoot) { Remove-Item -LiteralPath $fixtureRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path $agentRoot | Out-Null
Copy-Item -LiteralPath (Join-Path $canonicalAgent 'ARCHITECTURE.md') -Destination (Join-Path $agentRoot 'ARCHITECTURE.md') -Force
Copy-Item -LiteralPath (Join-Path $canonicalAgent 'framework_manifest.json') -Destination (Join-Path $agentRoot 'framework_manifest.json') -Force
Set-Content -LiteralPath (Join-Path $agentRoot 'local_only_marker.txt') -Value 'must be preserved in backup' -Encoding UTF8

$audit = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $cleanupScript -Mode Audit -ScopeRoots $fixtureRoot -OutputRoot $outputRoot | ConvertFrom-Json
Assert-True 'audit encontrou fixture' ($audit.candidates -eq 1)
Assert-True 'audit nao substituiu .agent' ((Get-Item -LiteralPath $agentRoot -Force).LinkType -notin @('Junction', 'SymbolicLink'))

$apply = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $cleanupScript -Mode Apply -ScopeRoots $fixtureRoot -OutputRoot $outputRoot | ConvertFrom-Json
$agentItem = Get-Item -LiteralPath $agentRoot -Force
$targets = @()
if ($agentItem.Target) { $targets = @($agentItem.Target) }
$actualTarget = if ($targets.Count -gt 0) { [string]$targets[0] } else { '' }
$backupManifest = Get-Content -LiteralPath $apply.backup_manifest_path -Raw -Encoding UTF8 | ConvertFrom-Json
$snapshotPath = [string]$backupManifest[0].snapshot_path

Assert-True 'apply substituiu por junction' ((($agentItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) -and ($agentItem.LinkType -in @('Junction', 'SymbolicLink')))
Assert-True 'junction aponta para .agent canonica' ([System.IO.Path]::GetFullPath($actualTarget) -eq [System.IO.Path]::GetFullPath($canonicalAgent)) ("Actual=$actualTarget")
Assert-True 'backup preservou arquivo local extra' (Test-Path -LiteralPath (Join-Path $snapshotPath 'local_only_marker.txt'))
Assert-True 'apply reportou zero falhas' ($apply.failed -eq 0)

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
