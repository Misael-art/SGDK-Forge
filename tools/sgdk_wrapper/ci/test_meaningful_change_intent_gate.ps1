<#
.SYNOPSIS
    Regression test for explicit blocker intent before another build.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$ScriptUnderTest = Join-Path $WrapperRoot "audit_meaningful_change.ps1"

function Assert-True {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if (-not $Condition) { throw $Message }
}

$ProjectRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("sgdk_meaningful_change_{0}" -f ([guid]::NewGuid().ToString("N")))
$LogDir = Join-Path $ProjectRoot "out\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

try {
    @{
        schema_version = "1.0.0"
        blocking_statuses = @("visual_gate_blocked", "visual_delivery_gate_missing")
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $LogDir "validation_report.json") -Encoding UTF8

    $reportPath = Join-Path $LogDir "meaningful_change_report.json"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest -ProjectRoot $ProjectRoot -RequireIntent -OutputPath $reportPath | Out-Null
    Assert-True ($LASTEXITCODE -ne 0) "Missing build intent should block when RequireIntent is active."
    $missingIntent = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    Assert-True ($missingIntent.blocker_code -eq "build_intent_missing") "Expected build_intent_missing."

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest `
        -ProjectRoot $ProjectRoot `
        -RequireIntent `
        -TargetBlocker "audio_missing" `
        -ChangeCategory "art" `
        -ChangeDiffSummary "Produce the first real Sector 01 visual fixture." `
        -OutputPath $reportPath | Out-Null
    Assert-True ($LASTEXITCODE -ne 0) "An intent targeting a non-current blocker should fail."
    $wrongTarget = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    Assert-True ($wrongTarget.blocker_code -eq "target_blocker_not_current") "Expected target_blocker_not_current."

    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest `
        -ProjectRoot $ProjectRoot `
        -RequireIntent `
        -TargetBlocker "visual_gate_blocked" `
        -ChangeCategory "art" `
        -ChangeDiffSummary "Produce the first real Sector 01 visual fixture." `
        -OutputPath $reportPath | Out-Null
    Assert-True ($LASTEXITCODE -eq 0) "A specific current blocker with an attacking change should pass."
    $validIntent = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    Assert-True ([bool]$validIntent.valid_progress) "Expected valid_progress for a specific visual change."

    Write-Host "[PASS] meaningful-change gate requires a specific current blocker and attacking change"
}
finally {
    Remove-Item -LiteralPath $ProjectRoot -Recurse -Force -ErrorAction SilentlyContinue
}
