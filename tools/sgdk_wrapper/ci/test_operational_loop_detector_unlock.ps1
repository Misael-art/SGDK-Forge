<#
.SYNOPSIS
    Regression test for detect_operational_loop.ps1 + operational_loop_decision.json unlock.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$ScriptUnderTest = Join-Path $WrapperRoot "detect_operational_loop.ps1"
if (-not (Test-Path -LiteralPath $ScriptUnderTest -PathType Leaf)) {
    throw "Script under test not found: $ScriptUnderTest"
}

function Assert-True {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if (-not $Condition) { throw $Message }
}

$ProjectRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("SGDK_LOOP_TEST_[{0}]" -f ([guid]::NewGuid().ToString("N")))
$DocDir = Join-Path $ProjectRoot "doc"
$LogDir = Join-Path $ProjectRoot "out\logs"
foreach ($p in @($DocDir, $LogDir)) { [System.IO.Directory]::CreateDirectory($p) | Out-Null }

$blockers = @("visual_gate_blocked")
$reportTemplate = @{
    schema_version = "1.0.0"
    generated_at = ""
    project_root = $ProjectRoot
    blocking_statuses = $blockers
    summary = @{ errors = 1 }
    errors = @(@{ code = "visual_gate_blocked" })
}

for ($i = 1; $i -le 3; $i++) {
    $report = $reportTemplate.Clone()
    $report.generated_at = ("2026-06-0{0}T00:00:0{0}Z" -f $i)
    $path = Join-Path $LogDir ("validation_report_{0}.json" -f $i)
    ($report | ConvertTo-Json -Depth 10) | Set-Content -LiteralPath $path -Encoding UTF8
}

$outPath = Join-Path $LogDir "operational_loop_report.json"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest -ProjectRoot $ProjectRoot -OutputPath $outPath | Out-Null
Assert-True ($LASTEXITCODE -ne 0) "Expected loop detector to block without operational_loop_decision.json"
Assert-True (Test-Path -LiteralPath $outPath -PathType Leaf) "Expected operational_loop_report.json to be written"

$decisionPath = Join-Path $DocDir "operational_loop_decision.json"
$decision = @{
    schema_version = "1.0.0"
    generated_at = "2026-06-06T12:00:00Z"
    project_root = $ProjectRoot
    owner = "human_owner"
    decision_date = "2026-06-06T12:00:00Z"
    dominant_blockers = @("visual_gate_blocked")
    strategy = "Stop infra churn and fix the dominant visual blocker with a measured capture loop."
    why_now_different = "New evidence exists for the current ROM hash and a human review is recorded."
    progress_justification = @{
        meaningful_change_summary = "Changed the art source and produced a fresh capture bundle for comparison."
    }
}
($decision | ConvertTo-Json -Depth 10) | Set-Content -LiteralPath $decisionPath -Encoding UTF8

powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest -ProjectRoot $ProjectRoot -OutputPath $outPath | Out-Null
Assert-True ($LASTEXITCODE -eq 0) "Expected loop detector to pass with valid operational_loop_decision.json"

$SingleReportProjectRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("SGDK_LOOP_SINGLE_[{0}]" -f ([guid]::NewGuid().ToString("N")))
$SingleDocDir = Join-Path $SingleReportProjectRoot "doc"
$SingleLogDir = Join-Path $SingleReportProjectRoot "out\logs"
foreach ($p in @($SingleDocDir, $SingleLogDir)) { [System.IO.Directory]::CreateDirectory($p) | Out-Null }

$singleReport = @{
    schema_version = "1.0.0"
    generated_at = "2026-06-06T12:00:00Z"
    project_root = $SingleReportProjectRoot
    blocking_statuses = @("visual_gate_blocked")
    summary = @{ errors = 1 }
    errors = @(@{ code = "visual_gate_blocked" })
}
($singleReport | ConvertTo-Json -Depth 10) | Set-Content -LiteralPath (Join-Path $SingleLogDir "validation_report.json") -Encoding UTF8

$singleOutPath = Join-Path $SingleLogDir "operational_loop_report.json"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest -ProjectRoot $SingleReportProjectRoot -OutputPath $singleOutPath | Out-Null
Assert-True ($LASTEXITCODE -eq 0) "Expected loop detector to pass and not crash with a single validation report"
Assert-True (Test-Path -LiteralPath $singleOutPath -PathType Leaf) "Expected single-report operational_loop_report.json to be written"

Write-Host "[PASS] operational loop detector blocks without decision and unlocks with decision"

$TempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd('\', '/')
$ResolvedFixture = [System.IO.Path]::GetFullPath($ProjectRoot)
if ($ResolvedFixture.StartsWith($TempRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    Remove-Item -LiteralPath $ResolvedFixture -Recurse -Force
}
$ResolvedSingleFixture = [System.IO.Path]::GetFullPath($SingleReportProjectRoot)
if ($ResolvedSingleFixture.StartsWith($TempRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    Remove-Item -LiteralPath $ResolvedSingleFixture -Recurse -Force
}
