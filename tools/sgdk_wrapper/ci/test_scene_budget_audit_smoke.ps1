<#
.SYNOPSIS
    Smoke test for audit_scene_budget.ps1 using aggregate runtime metrics.
.DESCRIPTION
    Creates a synthetic project with:
    - doc/scene-regression.json containing gameplay/result scenes sharing one app id
    - out/logs/runtime_metrics.json containing only top-level aggregate metrics
    Runs the budget auditor and verifies the explicit budget alias owner receives
    the aggregate metrics instead of the later result-state declaration.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File ci\test_scene_budget_audit_smoke.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
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

$tmpProj = Join-Path $env:TEMP "sgdk_budget_audit_smoke_$([guid]::NewGuid().ToString('N').Substring(0,8))"
$docDir = Join-Path $tmpProj 'doc'
$logsDir = Join-Path $tmpProj 'out\logs'
New-Item -ItemType Directory -Force -Path $docDir | Out-Null
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null

$manifest = @{
    schema_version = '1.0.0'
    scenes = @(
        @{
            scene_id = 'scene_multiplane_showcase_v2'
            expected_app_scene_id = 2
            budget_alias_owner = $true
        },
        @{
            scene_id = 'scene_multiplane_result_v2'
            expected_app_scene_id = 2
        }
    )
} | ConvertTo-Json -Depth 5
Set-Content -LiteralPath (Join-Path $docDir 'scene-regression.json') -Value $manifest -Encoding UTF8

$runtimeMetrics = @{
    schema_version = 1
    source = 'blastem_sram'
    capture_status = 'partial'
    scene_id = 2
    frames_seen = 151
    samples_recorded = 32
    over_budget_frames = 0
    max_scanline_sprites = 0
    sprite_engine_peak = 0
} | ConvertTo-Json -Depth 5
Set-Content -LiteralPath (Join-Path $logsDir 'runtime_metrics.json') -Value $runtimeMetrics -Encoding UTF8

Write-Host ''
Write-Host '=== Scene Budget Audit Smoke Test ==='
Write-Host ''

$runnerScript = Join-Path $wrapperRoot 'audit_scene_budget.ps1'
$reportPath = Join-Path $logsDir 'scene_budget_report.json'
$summaryPath = Join-Path $logsDir 'scene_budget_summary.md'
$exitCode = 0
try {
    & $runnerScript -ProjectRoot $tmpProj -WarnOnly 2>&1 | ForEach-Object { Write-Host "  > $_" }
    $exitCode = $LASTEXITCODE
} catch {
    Write-Host "  > Runner threw: $($_.Exception.Message)"
    $exitCode = 1
}

Write-Host ''
Write-Host '--- Assertions ---'

Assert-True 'Exit code 0 in warn-only mode' ($exitCode -eq 0) "got $exitCode"
Assert-True 'scene_budget_report.json exists' (Test-Path -LiteralPath $reportPath)
Assert-True 'scene_budget_summary.md exists' (Test-Path -LiteralPath $summaryPath)

$reportOk = $false
$report = $null
if (Test-Path -LiteralPath $reportPath) {
    try {
        $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $reportOk = $true
    } catch {}
}
Assert-True 'Report is valid JSON' $reportOk

if ($report) {
    $scenes = @($report.scenes)
    Assert-True 'Report emits both shared-id scenes' ($scenes.Count -eq 2) "got $($scenes.Count)"
    Assert-True 'Failure reason is no longer missing scene data' ($report.failure_reason -ne 'No scene data available for budget audit')

    $scene = $scenes | Where-Object { $_.scene_id -eq 'scene_multiplane_showcase_v2' } | Select-Object -First 1
    $resultScene = $scenes | Where-Object { $_.scene_id -eq 'scene_multiplane_result_v2' } | Select-Object -First 1
    Assert-True 'Scene id is preserved' ($scene -and $scene.scene_id -eq 'scene_multiplane_showcase_v2')
    Assert-True 'Aggregate-only metrics remain observational' ($scene -and $scene.budget_status -eq 'warn')
    Assert-True 'Measurement origin is measured' ($scene -and $scene.measurement_origin -eq 'measured')
    Assert-True 'Samples are surfaced as frames_analyzed' ($scene -and $scene.frames_analyzed -eq 32)
    Assert-True 'Explicit alias owner receives shared app-id metrics' ($scene -and $scene.frames_analyzed -eq 32)
    Assert-True 'Later result scene does not steal shared app-id metrics' ($resultScene -and $resultScene.measurement_origin -eq 'inferred')
}

Remove-Item -Recurse -Force $tmpProj -ErrorAction SilentlyContinue

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
