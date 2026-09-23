<#
.SYNOPSIS
    Focused test for degraded capture fields in scene_regression_report.json.
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

$libDir = Join-Path $wrapperRoot 'lib'
$contractsModule = Import-Module (Join-Path $libDir 'sgdk_artifact_contracts.psm1') -Force -PassThru
$sceneRegressionModule = Import-Module (Join-Path $libDir 'scene_regression.psm1') -Force -PassThru

$NewArtifactEnvelope = $contractsModule.ExportedCommands['New-SgdkArtifactEnvelope']
$WriteArtifactJson = $contractsModule.ExportedCommands['Write-SgdkJsonArtifact']
$NewSceneRegressionResult = $sceneRegressionModule.ExportedCommands['New-SceneRegressionResult']

$tmpRoot = Join-Path $env:TEMP "sgdk_regression_degraded_$([guid]::NewGuid().ToString('N').Substring(0,8))"
New-Item -ItemType Directory -Force -Path $tmpRoot | Out-Null
$reportPath = Join-Path $tmpRoot 'scene_regression_report.json'

Write-Host ''
Write-Host '=== Scene Regression Degraded Report Test ==='
Write-Host ''

$report = & $NewArtifactEnvelope `
    -ToolName 'run_scene_regression' `
    -ToolVersion '0.2.0' `
    -ProjectRoot 'C:\synthetic_project' `
    -WorkspaceRoot $wrapperRoot

$result = & $NewSceneRegressionResult `
    -SceneId 'degraded_scene' `
    -Status 'passed' `
    -ComparisonMode 'exact' `
    -CurrentRomSha256 ('a' * 64) `
    -EvidencePath 'out\evidence\degraded_scene' `
    -BaselinePath 'doc\baselines\degraded_scene' `
    -FailureReason 'Capture succeeded without readiness heartbeat' `
    -ReadinessOk $false `
    -CaptureStatus 'degraded' `
    -CaptureDegraded $true

$report['rom_sha256'] = ('a' * 64)
$report['scenes_total'] = 1
$report['scenes_passed'] = 1
$report['scenes_failed'] = 0
$report['scenes_errors'] = 0
$report['scenes_degraded'] = 1
$report['status'] = 'warn'
$report['failure_reason'] = '1 scene(s) were captured in degraded mode'
$report['results'] = @($result)

& $WriteArtifactJson -Data $report -Path $reportPath | Out-Null

$parsed = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

Assert-True 'Report JSON exists' (Test-Path -LiteralPath $reportPath)
Assert-True 'Report status=warn' ($parsed.status -eq 'warn')
Assert-True 'Report scenes_degraded=1' ($parsed.scenes_degraded -eq 1)
Assert-True 'Result count=1' (@($parsed.results).Count -eq 1)

$scene = @($parsed.results)[0]
Assert-True 'Result readiness_ok=false' ($scene.readiness_ok -eq $false)
Assert-True 'Result capture_status=degraded' ($scene.capture_status -eq 'degraded')
Assert-True 'Result capture_degraded=true' ($scene.capture_degraded -eq $true)
Assert-True 'Result status remains passed' ($scene.status -eq 'passed')

$schemaPath = Join-Path $wrapperRoot 'schemas\scene_regression_report.schema.json'
$validator = Join-Path $wrapperRoot 'validate_artifact_schema.ps1'
$validationOutput = & $validator -SchemaPath $schemaPath -ArtifactPath $reportPath 2>&1
Assert-True 'Report passes schema validation' ($LASTEXITCODE -eq 0) ($validationOutput -join '; ')

Remove-Item -Recurse -Force $tmpRoot -ErrorAction SilentlyContinue

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
