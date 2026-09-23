<#
.SYNOPSIS
    Standalone scene capture gate — validates whether a captured scene is valid.
.DESCRIPTION
    Reads artifacts from disk, validates MDRT, heartbeat, and required artifacts.
    Produces scene_capture_gate_report.json. This is the single authority for
    capture validity decisions.

    Does NOT compare baselines or judge visual regression — only decides if
    the capture is semantically valid and deterministic enough to enter the
    comparison pipeline.
.NOTES
    Observational tool. Can be called standalone or consumed by regression runner.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ProjectRoot,

    [Parameter(Mandatory)]
    [string]$SceneId,

    [Parameter(Mandatory = $false)]
    [string]$ManifestPath,

    [Parameter(Mandatory = $false)]
    [string]$EvidencePath,

    [Parameter(Mandatory = $false)]
    [switch]$WarnOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------
$ScriptRoot = $PSScriptRoot
$LibDir = Join-Path $ScriptRoot 'lib'

Import-Module (Join-Path $LibDir 'sgdk_artifact_contracts.psm1') -Force
Import-Module (Join-Path $LibDir 'scene_capture_gate.psm1') -Force

$contractsModule = Import-Module (Join-Path $LibDir 'sgdk_artifact_contracts.psm1') -Force -Global -PassThru
$NewArtifactEnvelope = $contractsModule.ExportedCommands['New-SgdkArtifactEnvelope']
$SetArtifactFailure = $contractsModule.ExportedCommands['Set-SgdkArtifactFailure']
$WriteArtifactJson = $contractsModule.ExportedCommands['Write-SgdkJsonArtifact']
$GetRomIdentity = $contractsModule.ExportedCommands['Get-SgdkRomIdentity']

$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)

if ([string]::IsNullOrWhiteSpace($ManifestPath)) {
    $ManifestPath = Join-Path $ProjectRoot 'doc\scene-regression.json'
}
if ([string]::IsNullOrWhiteSpace($EvidencePath)) {
    $EvidencePath = Join-Path $ProjectRoot "out\evidence\scenes\$SceneId"
}

$LogDir = Join-Path $ProjectRoot 'out\logs'
$ReportPath = Join-Path $LogDir 'scene_capture_gate_report.json'

# ---------------------------------------------------------------------------
# Artifact envelope
# ---------------------------------------------------------------------------
$artifact = & $NewArtifactEnvelope `
    -ToolName 'scene_capture_gate' `
    -ToolVersion '0.1.0' `
    -ProjectRoot $ProjectRoot

# ---------------------------------------------------------------------------
# Load manifest and find scene
# ---------------------------------------------------------------------------
$artifact['scene_id'] = $SceneId
$artifact['manifest_path'] = $ManifestPath
$artifact['evidence_path'] = $EvidencePath

if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
    & $SetArtifactFailure -Artifact $artifact -Reason "Manifest not found: $ManifestPath"
    $artifact['gate_result'] = $null
    & $WriteArtifactJson -Data $artifact -Path $ReportPath | Out-Null
    Write-Host "[FAIL] Manifest not found: $ManifestPath" -ForegroundColor Red
    if (-not $WarnOnly) { exit 1 }
    exit 0
}

try {
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
} catch {
    & $SetArtifactFailure -Artifact $artifact -Reason "Invalid JSON in manifest: $($_.Exception.Message)"
    $artifact['gate_result'] = $null
    & $WriteArtifactJson -Data $artifact -Path $ReportPath | Out-Null
    Write-Host "[FAIL] Invalid JSON: $($_.Exception.Message)" -ForegroundColor Red
    if (-not $WarnOnly) { exit 1 }
    exit 0
}

$sceneEntry = $manifest.scenes | Where-Object { $_.scene_id -eq $SceneId } | Select-Object -First 1
if (-not $sceneEntry) {
    & $SetArtifactFailure -Artifact $artifact -Reason "Scene '$SceneId' not found in manifest"
    $artifact['gate_result'] = $null
    & $WriteArtifactJson -Data $artifact -Path $ReportPath | Out-Null
    Write-Host "[FAIL] Scene '$SceneId' not found in manifest" -ForegroundColor Red
    if (-not $WarnOnly) { exit 1 }
    exit 0
}

# ---------------------------------------------------------------------------
# Compute ROM identity if available
# ---------------------------------------------------------------------------
$romSha256 = 'UNKNOWN'
$romPath = Join-Path $ProjectRoot 'out\rom.bin'
if (Test-Path -LiteralPath $romPath) {
    $romId = & $GetRomIdentity -RomPath $romPath
    $romSha256 = $romId.rom_sha256
}
$artifact['rom_sha256'] = $romSha256

# ---------------------------------------------------------------------------
# Run gate
# ---------------------------------------------------------------------------
if (-not (Test-Path -LiteralPath $EvidencePath -PathType Container)) {
    $gateResult = [ordered]@{
        scene_id                    = $SceneId
        expected_app_scene_id       = $null
        captured_app_scene_id       = $null
        scene_verification_required = $false
        scene_match                 = $null
        mdrt_present                = $false
        ready_heartbeat_ok          = $false
        readiness_ok                = $false
        artifacts_captured          = @()
        required_artifacts_present  = $false
        capture_status              = 'failed'
        failure_reason              = "Evidence directory not found: $EvidencePath"
    }
} else {
    $gateResult = Test-SceneCaptureSuccess `
        -SceneManifestEntry $sceneEntry `
        -EvidencePath $EvidencePath `
        -RomSha256 $romSha256
}

$artifact['gate_result'] = $gateResult

# ---------------------------------------------------------------------------
# Set artifact status based on gate
# ---------------------------------------------------------------------------
$captureStatus = $gateResult.capture_status

switch ($captureStatus) {
    'ok' {
        # artifact stays ok
    }
    'degraded' {
        & $SetArtifactFailure -Artifact $artifact -Reason $gateResult.failure_reason -Warn
    }
    'wrong_scene' {
        if ($WarnOnly) {
            & $SetArtifactFailure -Artifact $artifact -Reason $gateResult.failure_reason -Warn
        } else {
            & $SetArtifactFailure -Artifact $artifact -Reason $gateResult.failure_reason
        }
    }
    'failed' {
        if ($WarnOnly) {
            & $SetArtifactFailure -Artifact $artifact -Reason $gateResult.failure_reason -Warn
        } else {
            & $SetArtifactFailure -Artifact $artifact -Reason $gateResult.failure_reason
        }
    }
}

# ---------------------------------------------------------------------------
# Write report
# ---------------------------------------------------------------------------
& $WriteArtifactJson -Data $artifact -Path $ReportPath | Out-Null

# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------
Write-Host ''
$statusColor = switch ($captureStatus) {
    'ok'          { 'Green' }
    'degraded'    { 'Yellow' }
    'wrong_scene' { 'Red' }
    'failed'      { 'Red' }
}

$statusLabel = switch ($captureStatus) {
    'ok'          { 'PASS' }
    'degraded'    { 'DEGRADED' }
    'wrong_scene' { 'WRONG_SCENE' }
    'failed'      { 'FAIL' }
}

Write-Host "[$statusLabel] Scene '$SceneId': capture_status=$captureStatus" -ForegroundColor $statusColor

if ($gateResult.failure_reason) {
    Write-Host "  Reason: $($gateResult.failure_reason)" -ForegroundColor $statusColor
}

Write-Host "  Artifacts: $($gateResult.artifacts_captured -join ', ')"
Write-Host "  MDRT present: $($gateResult.mdrt_present)"
Write-Host "  Heartbeat: $($gateResult.ready_heartbeat_ok)"
Write-Host "  Scene match: $($gateResult.scene_match)"
Write-Host "  Report: $ReportPath"

if ($captureStatus -in @('failed', 'wrong_scene') -and -not $WarnOnly) {
    exit 1
}
exit 0
