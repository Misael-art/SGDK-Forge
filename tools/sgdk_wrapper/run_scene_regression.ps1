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
Import-Module (Join-Path $libDir 'scene_capture_gate.psm1') -Force -ErrorAction SilentlyContinue
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
$report['scenes'] = @()
$report['results'] = @()

$results = [System.Collections.ArrayList]::new()
$sceneReportRows = [System.Collections.ArrayList]::new()

function Convert-SceneResultToCanonicalStatus {
    param($Result)

    if ($null -eq $Result) {
        return 'failed'
    }

    $captureStatus = ''
    if ($Result -is [System.Collections.IDictionary]) {
        if ($Result.Contains('capture_status')) {
            $captureStatus = [string]$Result['capture_status']
        }
    } elseif ($Result.PSObject.Properties['capture_status']) {
        $captureStatus = [string]$Result.capture_status
    }

    $sceneMatch = $null
    if ($Result -is [System.Collections.IDictionary]) {
        if ($Result.Contains('scene_match')) {
            $sceneMatch = $Result['scene_match']
        }
    } elseif ($Result.PSObject.Properties['scene_match']) {
        $sceneMatch = $Result.scene_match
    }

    if (($captureStatus -eq 'ok' -or $captureStatus -eq 'degraded') -and $sceneMatch -ne $false) {
        return 'captured'
    }

    return 'failed'
}

# ---------------------------------------------------------------------------
# Helper: finalize and exit
# ---------------------------------------------------------------------------
function Complete-Report {
    param([bool]$HasFailures = $false)

    $uncapturedCount = @($sceneReportRows | Where-Object { $_.status -ne 'captured' }).Count
    if ($uncapturedCount -gt 0) {
        $HasFailures = $true
    }

    $report['scenes_total'] = $results.Count
    $report['scenes_passed'] = @($results | Where-Object { $_.status -eq 'passed' }).Count
    $report['scenes_failed'] = @($results | Where-Object { $_.status -eq 'failed' }).Count
    $report['scenes_errors'] = @($results | Where-Object { $_.status -eq 'error' }).Count
    $report['scenes_degraded'] = @($results | Where-Object { $_.capture_degraded -eq $true }).Count
    $report['scenes'] = @($sceneReportRows.ToArray())
    $report['results'] = @($results.ToArray())
    $report['summary'] = [ordered]@{
        scene_count = $results.Count
        failed_scene_keys = @($sceneReportRows | Where-Object { $_.status -ne 'captured' } | ForEach-Object { $_.scene_key })
        all_captured = (@($sceneReportRows | Where-Object { $_.status -ne 'captured' }).Count -eq 0)
    }

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
    if ($uncapturedCount -gt 0) {
        $reasonParts += "$uncapturedCount scene(s) were not captured"
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
    $sceneKey = if ($sceneConfig.PSObject.Properties['scene_key'] -and -not [string]::IsNullOrWhiteSpace([string]$sceneConfig.scene_key)) {
        [string]$sceneConfig.scene_key
    } else {
        [string]$sid
    }
    Write-Host "[INFO]  Scene: $sid"

    # Check bootstrap capability
    $bootstrap = Invoke-SceneBootstrap -SceneConfig $sceneConfig -ProjectRoot $ProjectRoot

    if (-not $bootstrap.Bootstrapped) {
        $r = New-SceneRegressionResult -SceneId $sid -Status 'unsupported' `
            -CurrentRomSha256 $romId.rom_sha256 `
            -FailureReason $bootstrap.Note
        [void]$results.Add($r)
        [void]$sceneReportRows.Add([ordered]@{
            scene_key = $sceneKey
            scene_id = $sid
            expected_app_scene_id = $null
            status = 'failed'
            captures = @(
                [ordered]@{
                    mode = 'default'
                    status = 'failed'
                    expected_scene_id = $null
                    captured_scene_id = $null
                    screenshot = $null
                    save_sram = $null
                    visual_vdp_dump = $null
                    bundle_json = $null
                    readiness_ok = $null
                    ready_heartbeat_ok = $null
                    scene_match = $null
                    failure_reason = $bootstrap.Note
                }
            )
        })
        Write-Host "  [SKIP] $($bootstrap.Note)"
        $hasFailures = $true
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
        [void]$sceneReportRows.Add([ordered]@{
            scene_key = $sceneKey
            scene_id = $sid
            expected_app_scene_id = $null
            status = 'failed'
            captures = @(
                [ordered]@{
                    mode = 'default'
                    status = 'failed'
                    expected_scene_id = $null
                    captured_scene_id = $null
                    screenshot = $null
                    save_sram = $null
                    visual_vdp_dump = $null
                    bundle_json = $null
                    readiness_ok = $null
                    ready_heartbeat_ok = $null
                    scene_match = $null
                    failure_reason = "BlastEm not found: $emulatorPath"
                }
            )
        })
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
            -NavigationSequence $bootstrap.NavigationSequence `
            -InitialSramBytes $bootstrap.InitialSramBytes
    } catch {
        $r = New-SceneRegressionResult -SceneId $sid -Status 'error' `
            -CurrentRomSha256 $romId.rom_sha256 `
            -EvidencePath $sceneEvidenceDir `
            -FailureReason "Capture error: $($_.Exception.Message)" `
            -CaptureStatus 'failed'
        [void]$results.Add($r)
        [void]$sceneReportRows.Add([ordered]@{
            scene_key = $sceneKey
            scene_id = $sid
            expected_app_scene_id = $null
            status = 'failed'
            captures = @(
                [ordered]@{
                    mode = 'default'
                    status = 'failed'
                    expected_scene_id = $null
                    captured_scene_id = $null
                    screenshot = $null
                    save_sram = $null
                    visual_vdp_dump = $null
                    bundle_json = $null
                    readiness_ok = $null
                    ready_heartbeat_ok = $null
                    scene_match = $null
                    failure_reason = "Capture error: $($_.Exception.Message)"
                }
            )
        })
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
            -ReadyHeartbeatOk $captureResult.ReadyHeartbeatOk `
            -CaptureStatus $captureResult.CaptureStatus `
            -CaptureDegraded ($captureResult.CaptureStatus -eq 'degraded') `
            -ExpectedAppSceneId $captureResult.ExpectedAppSceneId `
            -CapturedAppSceneId $captureResult.CapturedAppSceneId `
            -SceneMatch $captureResult.SceneMatch `
            -MdrtPresent $captureResult.MdrtPresent `
            -Artifacts $captureResult.Artifacts `
            -ArtifactPaths $captureResult.ArtifactPaths `
            -BundlePath $captureResult.BundlePath
        [void]$results.Add($r)
        [void]$sceneReportRows.Add([ordered]@{
            scene_key = $sceneKey
            scene_id = $sid
            expected_app_scene_id = $captureResult.ExpectedAppSceneId
            status = 'failed'
            captures = @(
                [ordered]@{
                    mode = 'default'
                    status = 'failed'
                    expected_scene_id = $captureResult.ExpectedAppSceneId
                    captured_scene_id = $captureResult.CapturedAppSceneId
                    screenshot = if ($captureResult.ArtifactPaths) { $captureResult.ArtifactPaths['screenshot'] } else { $null }
                    save_sram = if ($captureResult.ArtifactPaths) { $captureResult.ArtifactPaths['sram'] } else { $null }
                    visual_vdp_dump = if ($captureResult.ArtifactPaths) { $captureResult.ArtifactPaths['vdp_dump'] } else { $null }
                    bundle_json = $captureResult.BundlePath
                    readiness_ok = $captureResult.ReadinessOk
                    ready_heartbeat_ok = $captureResult.ReadyHeartbeatOk
                    scene_match = $captureResult.SceneMatch
                    failure_reason = $(if ($captureResult.Error) { $captureResult.Error } else { 'No artifacts captured' })
                }
            )
        })
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
        Get-ChildItem -LiteralPath $baselineRoot -File -ErrorAction SilentlyContinue | ForEach-Object {
            Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue
        }

        $baselineSources = [System.Collections.Generic.List[string]]::new()
        if ($captureResult.ArtifactPaths) {
            foreach ($artifactPath in $captureResult.ArtifactPaths.Values) {
                if ([string]::IsNullOrWhiteSpace([string]$artifactPath)) {
                    continue
                }
                $candidatePath = Join-Path $actualEvidenceDir ([string]$artifactPath)
                if (Test-Path -LiteralPath $candidatePath -PathType Leaf) {
                    [void]$baselineSources.Add($candidatePath)
                }
            }
        }
        if (-not [string]::IsNullOrWhiteSpace([string]$captureResult.BundlePath) -and (Test-Path -LiteralPath $captureResult.BundlePath -PathType Leaf)) {
            [void]$baselineSources.Add([string]$captureResult.BundlePath)
        }

        foreach ($sourcePath in ($baselineSources | Select-Object -Unique)) {
            [System.IO.File]::Copy(
                $sourcePath,
                (Join-Path $baselineRoot ([System.IO.Path]::GetFileName($sourcePath))),
                $true
            )
        }
        $r = New-SceneRegressionResult -SceneId $sid -Status 'passed' `
            -CurrentRomSha256 $romId.rom_sha256 `
            -EvidencePath $actualEvidenceDir `
            -BaselinePath $baselineRoot `
            -FailureReason 'Baseline updated' `
            -ReadinessOk $captureResult.ReadinessOk `
            -ReadyHeartbeatOk $captureResult.ReadyHeartbeatOk `
            -CaptureStatus $captureResult.CaptureStatus `
            -CaptureDegraded ($captureResult.CaptureStatus -eq 'degraded') `
            -ExpectedAppSceneId $captureResult.ExpectedAppSceneId `
            -CapturedAppSceneId $captureResult.CapturedAppSceneId `
            -SceneMatch $captureResult.SceneMatch `
            -MdrtPresent $captureResult.MdrtPresent `
            -Artifacts $captureResult.Artifacts `
            -ArtifactPaths $captureResult.ArtifactPaths `
            -BundlePath $captureResult.BundlePath
        [void]$results.Add($r)
        [void]$sceneReportRows.Add([ordered]@{
            scene_key = $sceneKey
            scene_id = $sid
            expected_app_scene_id = $captureResult.ExpectedAppSceneId
            status = $(Convert-SceneResultToCanonicalStatus -Result $r)
            captures = @(
                [ordered]@{
                    mode = 'default'
                    status = $(Convert-SceneResultToCanonicalStatus -Result $r)
                    expected_scene_id = $captureResult.ExpectedAppSceneId
                    captured_scene_id = $captureResult.CapturedAppSceneId
                    screenshot = if ($captureResult.ArtifactPaths) { $captureResult.ArtifactPaths['screenshot'] } else { $null }
                    save_sram = if ($captureResult.ArtifactPaths) { $captureResult.ArtifactPaths['sram'] } else { $null }
                    visual_vdp_dump = if ($captureResult.ArtifactPaths) { $captureResult.ArtifactPaths['vdp_dump'] } else { $null }
                    bundle_json = $captureResult.BundlePath
                    readiness_ok = $captureResult.ReadinessOk
                    ready_heartbeat_ok = $captureResult.ReadyHeartbeatOk
                    scene_match = $captureResult.SceneMatch
                    failure_reason = 'Baseline updated'
                }
            )
        })
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
        -ReadyHeartbeatOk $captureResult.ReadyHeartbeatOk `
        -CaptureStatus $captureResult.CaptureStatus `
        -CaptureDegraded ($captureResult.CaptureStatus -eq 'degraded') `
        -ExpectedAppSceneId $captureResult.ExpectedAppSceneId `
        -CapturedAppSceneId $captureResult.CapturedAppSceneId `
        -SceneMatch $captureResult.SceneMatch `
        -MdrtPresent $captureResult.MdrtPresent `
        -Artifacts $captureResult.Artifacts `
        -ArtifactPaths $captureResult.ArtifactPaths `
        -BundlePath $captureResult.BundlePath
    [void]$results.Add($r)
    $canonicalStatus = Convert-SceneResultToCanonicalStatus -Result $r
    [void]$sceneReportRows.Add([ordered]@{
        scene_key = $sceneKey
        scene_id = $sid
        expected_app_scene_id = $captureResult.ExpectedAppSceneId
        status = $canonicalStatus
        captures = @(
            [ordered]@{
                mode = 'default'
                status = $canonicalStatus
                expected_scene_id = $captureResult.ExpectedAppSceneId
                captured_scene_id = $captureResult.CapturedAppSceneId
                screenshot = if ($captureResult.ArtifactPaths) { $captureResult.ArtifactPaths['screenshot'] } else { $null }
                save_sram = if ($captureResult.ArtifactPaths) { $captureResult.ArtifactPaths['sram'] } else { $null }
                visual_vdp_dump = if ($captureResult.ArtifactPaths) { $captureResult.ArtifactPaths['vdp_dump'] } else { $null }
                bundle_json = $captureResult.BundlePath
                readiness_ok = $captureResult.ReadinessOk
                ready_heartbeat_ok = $captureResult.ReadyHeartbeatOk
                scene_match = $captureResult.SceneMatch
                failure_reason = $compResult.FailureReason
            }
        )
    })

    if ($compResult.Status -eq 'passed') {
        Write-Host "  [PASS] Matches baseline"
    } elseif ($compResult.Status -eq 'missing') {
        Write-Host "  [MISS] No baseline found at: $baselineRoot"
        $hasFailures = $true
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
        ready_heartbeat_ok = $r.ready_heartbeat_ok
        capture_status  = $r.capture_status
        capture_degraded = $r.capture_degraded
        expected_app_scene_id = $r.expected_app_scene_id
        captured_app_scene_id = $r.captured_app_scene_id
        scene_match     = $r.scene_match
        mdrt_present    = $r.mdrt_present
        artifacts       = $r.artifacts
        artifact_paths  = $r.artifact_paths
        bundle_path     = $r.bundle_path
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

$uncapturedExitCount = @($sceneReportRows | Where-Object { $_.status -ne 'captured' }).Count
if (($hasFailures -or $uncapturedExitCount -gt 0) -and -not $WarnOnly) { exit 1 }
exit 0
