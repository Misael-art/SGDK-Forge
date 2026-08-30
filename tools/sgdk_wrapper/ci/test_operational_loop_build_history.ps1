<#
.SYNOPSIS
    Regression test for operational-loop detection from canonical build snapshots.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$ScriptUnderTest = Join-Path $WrapperRoot "detect_operational_loop.ps1"

function Assert-True {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if (-not $Condition) { throw $Message }
}

function Write-BuildMeta {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][int]$Index
    )

    $buildDir = Join-Path $Root ("doc\changelog\roms\build_v{0:D3}" -f $Index)
    New-Item -ItemType Directory -Force -Path $buildDir | Out-Null
    $meta = [ordered]@{
        build_version = ("build_v{0:D3}" -f $Index)
        rom_sha256 = ("hash_{0:D3}" -f $Index)
        timestamp = ("2026-06-{0:D2}T00:00:00Z" -f $Index)
        validation_summary = [ordered]@{
            blocking_statuses = @(
                "visual_gate_blocked",
                "visual_delivery_gate_missing"
            )
        }
    }
    $meta | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $buildDir "build_meta.json") -Encoding UTF8
}

$ProjectRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("sgdk_loop_history_{0}" -f ([guid]::NewGuid().ToString("N")))
$LogDir = Join-Path $ProjectRoot "out\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

try {
    Write-BuildMeta -Root $ProjectRoot -Index 1
    Write-BuildMeta -Root $ProjectRoot -Index 2

    $reportPath = Join-Path $LogDir "operational_loop_report.json"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest -ProjectRoot $ProjectRoot -OutputPath $reportPath | Out-Null
    Assert-True ($LASTEXITCODE -eq 0) "Two repeated build snapshots should warn but not hard-block."
    $warningReport = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    Assert-True ([bool]$warningReport.progress_warning) "Expected progress_warning after two repeated snapshots."
    Assert-True (@($warningReport.builds_analyzed).Count -eq 2) "Expected two build snapshots to be analyzed."
    Assert-True (@($warningReport.builds_analyzed | Where-Object { $_.source_kind -eq "build_meta" }).Count -eq 2) "Expected build_meta history as the source."

    Write-BuildMeta -Root $ProjectRoot -Index 3
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest -ProjectRoot $ProjectRoot -OutputPath $reportPath | Out-Null
    Assert-True ($LASTEXITCODE -ne 0) "Three repeated build snapshots should hard-block."
    $blockedReport = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
    Assert-True ([bool]$blockedReport.loop_detected) "Expected loop_detected from build snapshots."
    Assert-True ($blockedReport.blocker_code -eq "operational_loop_detected") "Expected operational_loop_detected blocker."

    Write-Host "[PASS] operational loop detector uses canonical build snapshot history"
}
finally {
    Remove-Item -LiteralPath $ProjectRoot -Recurse -Force -ErrorAction SilentlyContinue
}
