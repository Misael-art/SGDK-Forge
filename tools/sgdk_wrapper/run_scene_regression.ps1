<#
.SYNOPSIS
    Runs deterministic scene regression tests against baselines.
.DESCRIPTION
    Standalone script for the AAA agent ecosystem. Reads a scene regression
    manifest, iterates declared scenes, captures evidence via BlastEm,
    compares with stored baselines, and produces a regression report.

    This script does NOT modify any existing wrapper behavior.
    It writes only to out/logs/ and out/evidence/scenes/.
.PARAMETER ProjectRoot
    Absolute path to the project root directory.
.PARAMETER ManifestPath
    Absolute path to scene-regression.json. Defaults to <ProjectRoot>/doc/scene-regression.json.
.PARAMETER SceneId
    Optional: run regression for a single scene only.
.PARAMETER EmulatorPath
    Optional override for BlastEm path. Defaults to the workspace BlastEm binary.
.PARAMETER UpdateBaseline
    If set, captured evidence replaces the current baseline instead of comparing.
.PARAMETER WarnOnly
    If set, failures produce warnings instead of error exit codes.
.EXAMPLE
    .\run_scene_regression.ps1 -ProjectRoot "C:\Projects\MyGame"
.EXAMPLE
    .\run_scene_regression.ps1 -ProjectRoot "C:\Projects\MyGame" -SceneId title_screen -UpdateBaseline
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ProjectRoot,
    [string]$ManifestPath,
    [string]$SceneId,
    [string]$EmulatorPath,
    [switch]$UpdateBaseline,
    [switch]$WarnOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ToolVersion = '0.1.0'

# ---------------------------------------------------------------------------
# Import modules
# ---------------------------------------------------------------------------
$libDir = Join-Path $PSScriptRoot 'lib'
Import-Module (Join-Path $libDir 'scene_regression.psm1') -Force
# Re-import contracts after scene_regression: the nested module import inside
# scene_regression otherwise hides the exported helpers from this script scope.
$contractsModule = Import-Module (Join-Path $libDir 'sgdk_artifact_contracts.psm1') -Force -Global -PassThru
$NewArtifactEnvelope = $contractsModule.ExportedCommands['New-SgdkArtifactEnvelope']
$SetArtifactFailure = $contractsModule.ExportedCommands['Set-SgdkArtifactFailure']
$WriteArtifactJson = $contractsModule.ExportedCommands['Write-SgdkJsonArtifact']
$GetRomIdentity = $contractsModule.ExportedCommands['Get-SgdkRomIdentity']

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot -ErrorAction Stop).Path

if ([string]::IsNullOrWhiteSpace($ManifestPath)) {
    $ManifestPath = Join-Path $ProjectRoot 'doc\scene-regression.json'
}

$workspaceRoot = $PSScriptRoot
for ($i = 0; $i -lt 5; $i++) {
    $workspaceRoot = Split-Path $workspaceRoot -Parent
    if (Test-Path (Join-Path $workspaceRoot 'CLAUDE.md')) { break }
}

$romPath = Join-Path $ProjectRoot 'out\rom.bin'
$emulatorPath = if ([string]::IsNullOrWhiteSpace($EmulatorPath)) {
    Join-Path $workspaceRoot 'tools\emuladores\BlastEm\blastem.exe'
} else {
    $EmulatorPath
}
$evidenceRoot = Join-Path $ProjectRoot 'out\evidence\scenes'
$logsDir = Join-Path $ProjectRoot 'out\logs'
$reportPath = Join-Path $logsDir 'scene_regression_report.json'
$matrixPath = Join-Path $logsDir 'scene_regression_matrix.json'

# ---------------------------------------------------------------------------
# Initialize report
# ---------------------------------------------------------------------------
$report = & $NewArtifactEnvelope `
    -ToolName 'run_scene_regression' `
    -ToolVersion $ToolVersion `
    -ProjectRoot $ProjectRoot `
    -WorkspaceRoot $workspaceRoot

$romId = & $GetRomIdentity -RomPath $romPath
$report['rom_sha256'] = $romId.rom_sha256
$report['scenes_total'] = 0
$report['scenes_passed'] = 0
$report['scenes_failed'] = 0
$report['scenes_errors'] = 0
$report['scenes_degraded'] = 0
$report['results'] = @()

$results = [System.Collections.ArrayList]::new()

# ---------------------------------------------------------------------------
# Helper: finalize and exit
# ---------------------------------------------------------------------------
function Complete-Report {
    param([bool]$HasFailures = $false)

    $report['scenes_total'] = $results.Count
    $report['scenes_passed'] = @($results | Where-Object { $_.status -eq 'passed' }).Count
    $report['scenes_failed'] = @($results | Where-Object { $_.status -eq 'failed' }).Count
    $report['scenes_errors'] = @($results | Where-Object { $_.status -eq 'error' }).Count
    $report['scenes_degraded'] = @($results | Where-Object { $_.capture_degraded -eq $true }).Count
    $report['results'] = @($results.ToArray())

    $reasonParts = @()
    if ($report['scenes_failed'] -gt 0) {
        $reasonParts += "$($report['scenes_failed']) scene(s) failed regression"
    }
    if ($report['scenes_errors'] -gt 0) {
        $reasonParts += "$($report['scenes_errors']) scene(s) had capture/runtime errors"
    }
    if ($report['scenes_degraded'] -gt 0) {
        $reasonParts += "$($report['scenes_degraded']) scene(s) were captured in degraded mode"
    }

    if ($HasFailures) {
        $report['status'] = if ($WarnOnly) { 'warn' } else { 'error' }
        $report['failure_reason'] = if ($reasonParts.Count -gt 0) { $reasonParts -join '; ' } else { 'Regression completed with failures' }
    } elseif ($report['scenes_degraded'] -gt 0) {
        $report['status'] = 'warn'
        $report['failure_reason'] = $reasonParts -join '; '
    }

    & $WriteArtifactJson -Data $report -Path $reportPath | Out-Null
}

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------
if (-not (Test-Path -LiteralPath $romPath)) {
    & $SetArtifactFailure -Artifact $report -Reason "ROM not found: $romPath" -Warn:$WarnOnly
    & $WriteArtifactJson -Data $report -Path $reportPath | Out-Null
    Write-Host "[$(if ($WarnOnly) {'WARN'} else {'ERROR'})] ROM not found: $romPath"
    if ($WarnOnly) { exit 0 } else { exit 1 }
}

# ---------------------------------------------------------------------------
# Load manifest
# ---------------------------------------------------------------------------
$manifest = Get-SceneRegressionManifest -ManifestPath $ManifestPath
if (-not $manifest) {
    & $SetArtifactFailure -Artifact $report -Reason "Cannot load regression manifest: $ManifestPath" -Warn:$WarnOnly
    & $WriteArtifactJson -Data $report -Path $reportPath | Out-Null
    Write-Host "[$(if ($WarnOnly) {'WARN'} else {'ERROR'})] Cannot load manifest: $ManifestPath"
    if ($WarnOnly) { exit 0 } else { exit 1 }
}

# Filter scenes
$scenes = @($manifest.scenes)
if (-not [string]::IsNullOrWhiteSpace($SceneId)) {
    $scenes = @($scenes | Where-Object { $_.scene_id -eq $SceneId })
    if ($scenes.Count -eq 0) {
        & $SetArtifactFailure -Artifact $report -Reason "Scene '$SceneId' not found in manifest" -Warn:$WarnOnly
        & $WriteArtifactJson -Data $report -Path $reportPath | Out-Null
        Write-Host "[$(if ($WarnOnly) {'WARN'} else {'ERROR'})] Scene '$SceneId' not in manifest"
        if ($WarnOnly) { exit 0 } else { exit 1 }
    }
}

Write-Host "[INFO]  Running regression for $($scenes.Count) scene(s) [mode=$(if ($UpdateBaseline) {'update_baseline'} else {'compare'})]"
$emulatorAvailable = Test-Path -LiteralPath $emulatorPath

# ---------------------------------------------------------------------------
# Process scenes
# ---------------------------------------------------------------------------
$hasFailures = $false

foreach ($sceneConfig in $scenes) {
    $sid = $sceneConfig.scene_id
    Write-Host "[INFO]  Scene: $sid"

    # Check bootstrap capability
    $bootstrap = Invoke-SceneBootstrap -SceneConfig $sceneConfig -ProjectRoot $ProjectRoot

    if (-not $bootstrap.Bootstrapped) {
        $r = New-SceneRegressionResult -SceneId $sid -Status 'unsupported' `
            -CurrentRomSha256 $romId.rom_sha256 `
            -FailureReason $bootstrap.Note
        [void]$results.Add($r)
        Write-Host "  [SKIP] $($bootstrap.Note)"
        continue
    }

    # Resolve baseline path
    $baselineRoot = if ($sceneConfig.PSObject.Properties['baseline_root']) {
        Join-Path $ProjectRoot $sceneConfig.baseline_root
    } else {
        Join-Path $ProjectRoot "doc\baselines\$sid"
    }

    if (-not $emulatorAvailable) {
        $r = New-SceneRegressionResult -SceneId $sid -Status 'error' `
            -CurrentRomSha256 $romId.rom_sha256 `
            -FailureReason "BlastEm not found: $emulatorPath" `
            -CaptureStatus 'failed'
        [void]$results.Add($r)
        Write-Host "  [ERROR] BlastEm not found: $emulatorPath"
        $hasFailures = $true
        continue
    }

    # Capture evidence — evidence dir is evidenceRoot/<scene_id>
    $sceneEvidenceDir = Join-Path $evidenceRoot $sid
    $captureResult = $null

    try {
        $captureResult = Invoke-SceneCapture `
            -SceneConfig $sceneConfig `
            -ProjectRoot $ProjectRoot `
            -OutputRoot $sceneEvidenceDir `
            -EmulatorPath $emulatorPath `
            -RomPath $romPath `
            -NavigationSequence $bootstrap.NavigationSequence
    } catch {
        $r = New-SceneRegressionResult -SceneId $sid -Status 'error' `
            -CurrentRomSha256 $romId.rom_sha256 `
            -EvidencePath $sceneEvidenceDir `
            -FailureReason "Capture error: $($_.Exception.Message)" `
            -CaptureStatus 'failed'
        [void]$results.Add($r)
        Write-Host "  [ERROR] Capture failed: $($_.Exception.Message)"
        $hasFailures = $true
        continue
    }

    if (-not $captureResult.Captured) {
        $r = New-SceneRegressionResult -SceneId $sid -Status 'error' `
            -CurrentRomSha256 $romId.rom_sha256 `
            -EvidencePath $sceneEvidenceDir `
            -FailureReason $(if ($captureResult.Error) { $captureResult.Error } else { 'No artifacts captured' }) `
            -ReadinessOk $captureResult.ReadinessOk `
            -CaptureStatus $captureResult.CaptureStatus `
            -CaptureDegraded ($captureResult.CaptureStatus -eq 'degraded')
        [void]$results.Add($r)
        Write-Host "  [ERROR] No artifacts captured"
        $hasFailures = $true
        continue
    }

    # Warn if readiness was not confirmed
    if (-not $captureResult.ReadinessOk) {
        Write-Host "  [WARN] Capture proceeded without readiness heartbeat (degraded)"
    }

    # Use evidence path from capture result (canonical location)
    $actualEvidenceDir = $captureResult.EvidencePath

    # Update baseline mode
    if ($UpdateBaseline) {
        if (-not (Test-Path -LiteralPath $baselineRoot)) {
            New-Item -ItemType Directory -Force -Path $baselineRoot | Out-Null
        }
        # Copy evidence to baseline
        Get-ChildItem -LiteralPath $actualEvidenceDir -File -ErrorAction SilentlyContinue | ForEach-Object {
            Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $baselineRoot $_.Name) -Force
        }
        $r = New-SceneRegressionResult -SceneId $sid -Status 'passed' `
            -CurrentRomSha256 $romId.rom_sha256 `
            -EvidencePath $actualEvidenceDir `
            -BaselinePath $baselineRoot `
            -FailureReason 'Baseline updated' `
            -ReadinessOk $captureResult.ReadinessOk `
            -CaptureStatus $captureResult.CaptureStatus `
            -CaptureDegraded ($captureResult.CaptureStatus -eq 'degraded')
        [void]$results.Add($r)
        Write-Host "  [OK]   Baseline updated at: $baselineRoot"
        continue
    }

    # Compare mode
    $compResult = Compare-SceneEvidence -SceneConfig $sceneConfig -EvidencePath $actualEvidenceDir -BaselinePath $baselineRoot
    $compMode = if ($sceneConfig.PSObject.Properties['comparison_mode']) { $sceneConfig.comparison_mode } else { 'exact' }

    $r = New-SceneRegressionResult -SceneId $sid -Status $compResult.Status `
        -ComparisonMode $compMode `
        -CurrentRomSha256 $romId.rom_sha256 `
        -DiffSummary $compResult.DiffSummary `
        -EvidencePath $actualEvidenceDir `
        -BaselinePath $baselineRoot `
        -FailureReason $compResult.FailureReason `
        -ReadinessOk $captureResult.ReadinessOk `
        -CaptureStatus $captureResult.CaptureStatus `
        -CaptureDegraded ($captureResult.CaptureStatus -eq 'degraded')
    [void]$results.Add($r)

    if ($compResult.Status -eq 'passed') {
        Write-Host "  [PASS] Matches baseline"
    } elseif ($compResult.Status -eq 'missing') {
        Write-Host "  [MISS] No baseline found at: $baselineRoot"
    } else {
        Write-Host "  [FAIL] $($compResult.FailureReason)"
        $hasFailures = $true
    }
}

# ---------------------------------------------------------------------------
# Finalize
# ---------------------------------------------------------------------------
Complete-Report -HasFailures $hasFailures

# ---------------------------------------------------------------------------
# Generate regression matrix (scene_regression_matrix.json)
# ---------------------------------------------------------------------------
$matrix = & $NewArtifactEnvelope `
    -ToolName 'run_scene_regression' `
    -ToolVersion $ToolVersion `
    -ProjectRoot $ProjectRoot `
    -WorkspaceRoot $workspaceRoot

$matrix['rom_sha256'] = $romId.rom_sha256
$matrix['matrix'] = @{}
foreach ($r in $results) {
    $matrix['matrix'][$r.scene_id] = [ordered]@{
        status          = $r.status
        comparison_mode = $r.comparison_mode
        evidence_path   = $r.evidence_path
        baseline_path   = $r.baseline_path
        diff_summary    = $r.diff_summary
        readiness_ok    = $r.readiness_ok
        capture_status  = $r.capture_status
        capture_degraded = $r.capture_degraded
    }
}
& $WriteArtifactJson -Data $matrix -Path $matrixPath | Out-Null

$passed = @($results | Where-Object { $_.status -eq 'passed' }).Count
$failed = @($results | Where-Object { $_.status -eq 'failed' }).Count
$missing = @($results | Where-Object { $_.status -eq 'missing' }).Count
$unsup = @($results | Where-Object { $_.status -eq 'unsupported' }).Count
$errs = @($results | Where-Object { $_.status -eq 'error' }).Count

Write-Host "[$($report['status'].ToString().ToUpper())] Regression: $($results.Count) scene(s) [P:$passed F:$failed M:$missing U:$unsup E:$errs]"
Write-Host "[INFO]  Report: $reportPath"
Write-Host "[INFO]  Matrix: $matrixPath"

if ($hasFailures -and -not $WarnOnly) { exit 1 }
exit 0
