<#
.SYNOPSIS
    Smoke test for tools/sgdk_wrapper/scene_closeout_gate.ps1 plan mode.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$ScriptUnderTest = Join-Path $WrapperRoot "scene_closeout_gate.ps1"
if (-not (Test-Path -LiteralPath $ScriptUnderTest -PathType Leaf)) {
    throw "Script under test not found: $ScriptUnderTest"
}

function Assert-True {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )

    if (-not $Condition) {
        throw $Message
    }
}

$ProjectRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("sgdk_scene_closeout_gate_test_{0}" -f ([guid]::NewGuid().ToString("N")))
$DocDir = Join-Path $ProjectRoot "doc"
$LogDir = Join-Path $ProjectRoot "out\logs"
New-Item -ItemType Directory -Force -Path $DocDir, $LogDir | Out-Null

[System.IO.File]::WriteAllText((Join-Path $DocDir "13-spec-cenas.md"), "# spec`n", [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllText((Join-Path $ProjectRoot "build.bat"), "@echo off`r`nexit /b 0`r`n", [System.Text.Encoding]::ASCII)

& $ScriptUnderTest -ProjectRoot $ProjectRoot -SceneId "front_end_main_menu" -TargetScene 1 -PlanOnly
if ($LASTEXITCODE -ne 0) {
    throw "scene_closeout_gate.ps1 plan mode exited with code $LASTEXITCODE"
}

$ReportPath = Join-Path $LogDir "scene_closeout_gate_report.json"
Assert-True (Test-Path -LiteralPath $ReportPath -PathType Leaf) "scene_closeout_gate_report.json was not written"
$report = Get-Content -LiteralPath $ReportPath -Raw | ConvertFrom-Json

Assert-True ($report.closeout_status -eq "planned") "Expected closeout_status planned, got '$($report.closeout_status)'"
Assert-True ($report.status -eq "ok") "Expected common status ok, got '$($report.status)'"
Assert-True ([int]$report.summary.planned -ge 1) "Expected planned steps"

$stepNames = @($report.steps | ForEach-Object { $_.name })
foreach ($expected in @("build", "scene_contract_compiler", "res_graph_audit", "validate_resources", "runtime_capture", "screenshot_semantic_gate", "scene_regression", "promotion_claim_audit", "fresh_evidence_bundle_audit", "freshness_audit", "doc_sync_audit", "evidence_finalize")) {
    Assert-True ($stepNames -contains $expected) "Expected planned step '$expected'"
}
$compilerStep = $report.steps | Where-Object { $_.name -eq "scene_contract_compiler" } | Select-Object -First 1
Assert-True ($compilerStep -and (@($compilerStep.arguments) -contains "production")) "Expected closeout compiler to use production mode"

$BlockedProjectRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("sgdk_scene_closeout_blocked_test_{0}" -f ([guid]::NewGuid().ToString("N")))
$BlockedDocDir = Join-Path $BlockedProjectRoot "doc"
$BlockedLogDir = Join-Path $BlockedProjectRoot "out\logs"
New-Item -ItemType Directory -Force -Path $BlockedDocDir, $BlockedLogDir, (Join-Path $BlockedProjectRoot "res"), (Join-Path $BlockedProjectRoot "src"), (Join-Path $BlockedDocDir "changelog") | Out-Null

[System.IO.File]::WriteAllText((Join-Path $BlockedDocDir "13-spec-cenas.md"), "# spec`n", [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllText((Join-Path $BlockedDocDir "changelog\changelog.md"), "# changelog`n", [System.Text.Encoding]::UTF8)

$FakeToolDir = Join-Path ([System.IO.Path]::GetTempPath()) ("sgdk_scene_closeout_fake_tools_{0}" -f ([guid]::NewGuid().ToString("N")))
New-Item -ItemType Directory -Force -Path $FakeToolDir | Out-Null
[System.IO.File]::WriteAllText((Join-Path $FakeToolDir "py.bat"), "@echo off`r`nexit /b 0`r`n", [System.Text.Encoding]::ASCII)
$OriginalPath = $env:PATH
$env:PATH = "$FakeToolDir$([System.IO.Path]::PathSeparator)$env:PATH"

& $ScriptUnderTest -ProjectRoot $BlockedProjectRoot -SceneId "visual_gate_fixture" -SkipBuild -SkipRuntimeCapture -SkipSceneRegression
$blockedNoWarnExit = $LASTEXITCODE

$BlockedReportPath = Join-Path $BlockedLogDir "scene_closeout_gate_report.json"
Assert-True ($blockedNoWarnExit -ne 0) "Expected blocked fixture without WarnOnly to exit non-zero"
Assert-True (Test-Path -LiteralPath $BlockedReportPath -PathType Leaf) "blocked fixture scene_closeout_gate_report.json was not written"
$blockedNoWarnReport = Get-Content -LiteralPath $BlockedReportPath -Raw | ConvertFrom-Json

Assert-True ($blockedNoWarnReport.closeout_status -eq "blocked") "Expected closeout_status blocked without WarnOnly, got '$($blockedNoWarnReport.closeout_status)'"
Assert-True ($blockedNoWarnReport.status -eq "error") "Expected common status error without WarnOnly, got '$($blockedNoWarnReport.status)'"
Assert-True (@($blockedNoWarnReport.summary.validation_blocking_statuses | Where-Object { $_ -eq "visual_gate_blocked" }).Count -gt 0) "Expected visual_gate_blocked in no-WarnOnly closeout summary"

& $ScriptUnderTest -ProjectRoot $BlockedProjectRoot -SceneId "visual_gate_fixture" -SkipBuild -SkipRuntimeCapture -SkipSceneRegression -WarnOnly
if ($LASTEXITCODE -ne 0) {
    throw "scene_closeout_gate.ps1 blocked fixture exited with code $LASTEXITCODE"
}

Assert-True (Test-Path -LiteralPath $BlockedReportPath -PathType Leaf) "blocked fixture scene_closeout_gate_report.json was not written"
$blockedReport = Get-Content -LiteralPath $BlockedReportPath -Raw | ConvertFrom-Json

Assert-True ($blockedReport.closeout_status -eq "blocked") "Expected closeout_status blocked, got '$($blockedReport.closeout_status)'"
Assert-True ($blockedReport.status -eq "warn") "Expected common status warn, got '$($blockedReport.status)'"
Assert-True (@($blockedReport.summary.validation_blocking_statuses | Where-Object { $_ -eq "visual_gate_blocked" }).Count -gt 0) "Expected visual_gate_blocked in closeout summary"

$env:PATH = $OriginalPath
Remove-Item -LiteralPath $FakeToolDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "[PASS] scene_closeout_gate plan mode exposes canonical closeout sequence"
Write-Host "[INFO] Temp project retained for inspection: $ProjectRoot"
Write-Host "[PASS] scene_closeout_gate reports blocked/error without WarnOnly"
Write-Host "[PASS] scene_closeout_gate reports blocked when validation_report has blockers"
Write-Host "[INFO] Temp blocked project retained for inspection: $BlockedProjectRoot"
