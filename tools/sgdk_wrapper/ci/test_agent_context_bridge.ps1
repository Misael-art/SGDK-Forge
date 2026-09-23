<#
.SYNOPSIS
    Verifica que .agents/skills e apenas ponte para a arvore canonica.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$bridgePath = Join-Path $workspaceRoot '.agents\skills'
$expectedTarget = Join-Path $workspaceRoot 'tools\sgdk_wrapper\.agent\skills'

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
Write-Host '=== Agent Context Bridge Test ==='
Write-Host ''

$bridge = Get-Item -LiteralPath $bridgePath -Force
$targets = @()
if ($bridge.Target) { $targets = @($bridge.Target) }
$actualTarget = if ($targets.Count -gt 0) { [string]$targets[0] } else { '' }
$tracked = @(git -C $workspaceRoot ls-files '.agents/skills/**')

Assert-True '.agents/skills existe' (Test-Path -LiteralPath $bridgePath)
Assert-True '.agents/skills e junction/symlink' ((($bridge.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) -and ($bridge.LinkType -in @('Junction', 'SymbolicLink'))) ("LinkType=$($bridge.LinkType)")
Assert-True '.agents/skills aponta para skills canonicas' ([System.IO.Path]::GetFullPath($actualTarget) -eq [System.IO.Path]::GetFullPath($expectedTarget)) ("Actual=$actualTarget")
Assert-True '.agents/skills nao possui conteudo rastreado no Git' ($tracked.Count -eq 0) (($tracked | Select-Object -First 5) -join ', ')

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
