<#
.SYNOPSIS
    Guards the split between capture presence requirements and baseline diff inputs.
.DESCRIPTION
    Verifies that:
    1. `required_artifacts` does not implicitly force SRAM into binary comparison.
    2. `comparison_artifacts` explicitly controls which artifacts are diffed.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
Import-Module (Join-Path $wrapperRoot 'lib\scene_regression.psm1') -Force

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

$tmpRoot = Join-Path $env:TEMP "sgdk_regression_artifact_split_$([guid]::NewGuid().ToString('N').Substring(0,8))"
$baselineDir = Join-Path $tmpRoot 'baseline'
$evidenceDir = Join-Path $tmpRoot 'evidence'
New-Item -ItemType Directory -Force -Path $baselineDir | Out-Null
New-Item -ItemType Directory -Force -Path $evidenceDir | Out-Null

try {
    $sharedScreenshot = [byte[]](137,80,78,71,13,10,26,10,0,0,0,0)
    [System.IO.File]::WriteAllBytes((Join-Path $baselineDir 'screenshot.png'), $sharedScreenshot)
    [System.IO.File]::WriteAllBytes((Join-Path $evidenceDir 'screenshot.png'), $sharedScreenshot)

    [System.IO.File]::WriteAllBytes((Join-Path $baselineDir 'save.sram'), [byte[]](1,2,3,4))
    [System.IO.File]::WriteAllBytes((Join-Path $evidenceDir 'save.sram'), [byte[]](9,8,7,6))

    Write-Host ''
    Write-Host '=== Scene Regression Artifact Split Test ==='
    Write-Host ''

    $presenceOnlyConfig = [pscustomobject]@{
        scene_id             = 'presence_only_scene'
        comparison_mode      = 'exact'
        required_artifacts   = @('screenshot', 'sram')
        comparison_artifacts = @('screenshot')
    }

    $presenceOnlyResult = Compare-SceneEvidence `
        -SceneConfig $presenceOnlyConfig `
        -EvidencePath $evidenceDir `
        -BaselinePath $baselineDir

    Assert-True 'Presence-only config passes when screenshot matches' ($presenceOnlyResult.Status -eq 'passed') ($presenceOnlyResult.FailureReason)
    Assert-True 'Presence-only config keeps screenshot_match=true' ($presenceOnlyResult.DiffSummary.screenshot_match -eq $true)
    Assert-True 'Presence-only config does not diff SRAM' ($null -eq $presenceOnlyResult.DiffSummary.sram_match)

    $explicitSramCompareConfig = [pscustomobject]@{
        scene_id             = 'explicit_sram_scene'
        comparison_mode      = 'exact'
        required_artifacts   = @('screenshot', 'sram')
        comparison_artifacts = @('screenshot', 'sram')
    }

    $explicitSramCompareResult = Compare-SceneEvidence `
        -SceneConfig $explicitSramCompareConfig `
        -EvidencePath $evidenceDir `
        -BaselinePath $baselineDir

    Assert-True 'Explicit SRAM compare fails on binary mismatch' ($explicitSramCompareResult.Status -eq 'failed') ($explicitSramCompareResult.FailureReason)
    Assert-True 'Explicit SRAM compare records sram_match=false' ($explicitSramCompareResult.DiffSummary.sram_match -eq $false)
    Assert-True 'Explicit SRAM compare reports SRAM mismatch' ($explicitSramCompareResult.FailureReason -eq 'SRAM mismatch')
}
finally {
    Remove-Item -Recurse -Force $tmpRoot -ErrorAction SilentlyContinue
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
