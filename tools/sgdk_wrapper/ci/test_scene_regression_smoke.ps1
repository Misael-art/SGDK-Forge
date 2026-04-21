<#
.SYNOPSIS
    Smoke test for run_scene_regression.ps1 — validates report and matrix creation.
.DESCRIPTION
    Creates a synthetic project with a fake ROM and manifest.
    Runs the regression runner and verifies:
    1. scene_regression_report.json is created with correct schema fields
    2. scene_regression_matrix.json is created with correct schema fields
    3. Unsupported scenes are recorded as "unsupported"
    4. Direct-boot scenes surface a non-success status without aborting the run
    5. -WarnOnly flag produces exit code 0 even on errors or misses

    Does NOT require a valid ROM and remains valid whether BlastEm is installed
    or absent on the host — it exercises the report/matrix scaffolding path.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File ci\test_scene_regression_smoke.ps1
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

# ---------------------------------------------------------------------------
# Setup synthetic project
# ---------------------------------------------------------------------------
$tmpProj = Join-Path $env:TEMP "sgdk_regression_smoke_$([guid]::NewGuid().ToString('N').Substring(0,8))"
$docDir = Join-Path $tmpProj 'doc'
$outDir = Join-Path $tmpProj 'out'
$logsDir = Join-Path $outDir 'logs'
New-Item -ItemType Directory -Force -Path $docDir | Out-Null
New-Item -ItemType Directory -Force -Path $logsDir | Out-Null

# Fake ROM (just 512 bytes of zeros — enough for sha256)
$romPath = Join-Path $outDir 'rom.bin'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
[System.IO.File]::WriteAllBytes($romPath, (New-Object byte[] 512))

# Regression manifest with one unsupported and one direct_boot scene
$manifest = @{
    schema_version = '1.0.0'
    scenes = @(
        @{
            scene_id        = 'unsupported_scene'
            boot_mode       = 'unsupported'
            capture_kind    = 'screenshot'
        },
        @{
            scene_id        = 'direct_scene'
            boot_mode       = 'direct_boot'
            capture_kind    = 'screenshot'
            capture_frame   = 60
            comparison_mode = 'exact'
        }
    )
} | ConvertTo-Json -Depth 5
Set-Content -LiteralPath (Join-Path $docDir 'scene-regression.json') -Value $manifest -Encoding UTF8

Write-Host ''
Write-Host '=== Scene Regression Smoke Test ==='
Write-Host ''

# ---------------------------------------------------------------------------
# Run regression and validate report/matrix generation in warn-only mode.
# ---------------------------------------------------------------------------
$reportPath = Join-Path $logsDir 'scene_regression_report.json'
$matrixPath = Join-Path $logsDir 'scene_regression_matrix.json'

# Run with -WarnOnly so it exits 0 even on capture failure.
# Force a nonexistent emulator path so the result is deterministic on any host.
# Invoke in-process (not child powershell) so module imports resolve correctly
$runnerScript = Join-Path $wrapperRoot 'run_scene_regression.ps1'
$fakeEmulatorPath = Join-Path $tmpProj 'missing_blastem.exe'
$exitCode = 0
try {
    & $runnerScript -ProjectRoot $tmpProj -EmulatorPath $fakeEmulatorPath -WarnOnly 2>&1 | ForEach-Object { Write-Host "  > $_" }
    $exitCode = $LASTEXITCODE
} catch {
    Write-Host "  > Runner threw: $($_.Exception.Message)"
    $exitCode = 1
}

Write-Host ''
Write-Host '--- Assertions ---'

# 1. Exit code 0 with -WarnOnly
Assert-True 'Exit code 0 with -WarnOnly' ($exitCode -eq 0) "got $exitCode"

# 2. Report file exists
Assert-True 'scene_regression_report.json exists' (Test-Path -LiteralPath $reportPath)

# 3. Matrix file exists
Assert-True 'scene_regression_matrix.json exists' (Test-Path -LiteralPath $matrixPath)

# 4. Parse report
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
    # 5. Required envelope fields
    Assert-True 'Report has schema_version' ($null -ne $report.schema_version)
    Assert-True 'Report has tool_name=run_scene_regression' ($report.tool_name -eq 'run_scene_regression')
    Assert-True 'Report has rom_sha256' ($null -ne $report.rom_sha256 -and $report.rom_sha256.Length -gt 0)
    Assert-True 'Report has results array' ($null -ne $report.results)

    # 6. Check scene results
    $resultsList = @($report.results)
    Assert-True 'Report contains 2 scene results' ($resultsList.Count -eq 2)

    $unsup = $resultsList | Where-Object { $_.scene_id -eq 'unsupported_scene' } | Select-Object -First 1
    Assert-True 'Unsupported scene status=unsupported' ($unsup -and $unsup.status -eq 'unsupported')

    $direct = $resultsList | Where-Object { $_.scene_id -eq 'direct_scene' } | Select-Object -First 1
    Assert-True 'Direct scene status=error with missing emulator' ($direct -and $direct.status -eq 'error')
    Assert-True 'Direct scene capture_status=failed' ($direct -and $direct.capture_status -eq 'failed')
    Assert-True 'Direct scene capture_degraded=false' ($direct -and $direct.capture_degraded -eq $false)
    Assert-True 'Direct scene failure_reason mentions BlastEm' ($direct -and $direct.failure_reason -like '*BlastEm not found*')
    Assert-True 'Report degraded count stays zero in missing-emulator path' ($report.scenes_degraded -eq 0)
}

# 7. Parse matrix
$matrixOk = $false
$matrix = $null
if (Test-Path -LiteralPath $matrixPath) {
    try {
        $matrix = Get-Content -LiteralPath $matrixPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $matrixOk = $true
    } catch {}
}
Assert-True 'Matrix is valid JSON' $matrixOk

if ($matrix) {
    Assert-True 'Matrix has schema_version' ($null -ne $matrix.schema_version)
    Assert-True 'Matrix has rom_sha256' ($null -ne $matrix.rom_sha256)
    Assert-True 'Matrix has matrix object' ($null -ne $matrix.matrix)

    # Check matrix entries
    $hasUnsup = $null -ne $matrix.matrix.PSObject.Properties['unsupported_scene']
    Assert-True 'Matrix contains unsupported_scene entry' $hasUnsup

    $hasDirect = $null -ne $matrix.matrix.PSObject.Properties['direct_scene']
    Assert-True 'Matrix contains direct_scene entry' $hasDirect

    if ($hasDirect) {
        $directMatrix = $matrix.matrix.direct_scene
        Assert-True 'Matrix exposes capture_status field' ($null -ne $directMatrix.capture_status)
        Assert-True 'Matrix exposes capture_degraded field' ($null -ne $directMatrix.capture_degraded)
    }
}

# 8. Validate report against schema
$schemaPath = Join-Path $wrapperRoot 'schemas\scene_regression_report.schema.json'
if ((Test-Path -LiteralPath $schemaPath) -and (Test-Path -LiteralPath $reportPath)) {
    $valScript = Join-Path $wrapperRoot 'validate_artifact_schema.ps1'
    $valResult = & $valScript -SchemaPath $schemaPath -ArtifactPath $reportPath 2>&1
    Assert-True 'Report passes schema validation' ($LASTEXITCODE -eq 0) ($valResult -join '; ')
}

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------
Remove-Item -Recurse -Force $tmpProj -ErrorAction SilentlyContinue

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
