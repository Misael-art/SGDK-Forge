<#
.SYNOPSIS
    Audits per-scene budget usage against hardware limits.
.DESCRIPTION
    Standalone script for the AAA agent ecosystem. Consolidates metric data,
    evaluates each scene against budget thresholds, and produces a report
    that clearly marks what was measured vs estimated vs inferred.

    This script does NOT modify any existing wrapper behavior.
    It writes only to out/logs/.

    DECISION PENDING: Canonical thresholds per scene type are not yet defined.
    Current thresholds are conservative observation-mode defaults.
.PARAMETER ProjectRoot
    Absolute path to the project root directory.
.PARAMETER RuntimeMetricsPath
    Absolute path to runtime_metrics.json. Auto-discovered if omitted.
.PARAMETER SceneId
    Optional: audit a single scene only.
.PARAMETER WarnOnly
    If set, budget violations produce warnings instead of error exit codes.
.EXAMPLE
    .\audit_scene_budget.ps1 -ProjectRoot "C:\Projects\MyGame"
.EXAMPLE
    .\audit_scene_budget.ps1 -ProjectRoot "C:\Projects\MyGame" -SceneId gameplay_stage1
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ProjectRoot,
    [string]$RuntimeMetricsPath,
    [string]$SceneId,
    [switch]$WarnOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ToolVersion = '0.1.0'

# ---------------------------------------------------------------------------
# Import modules
# ---------------------------------------------------------------------------
$libDir = Join-Path $PSScriptRoot 'lib'
Import-Module (Join-Path $libDir 'sgdk_artifact_contracts.psm1') -Force
Import-Module (Join-Path $libDir 'scene_budget.psm1') -Force

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot -ErrorAction Stop).Path

if ([string]::IsNullOrWhiteSpace($RuntimeMetricsPath)) {
    $RuntimeMetricsPath = Join-Path $ProjectRoot 'out\logs\runtime_metrics.json'
}

$workspaceRoot = $PSScriptRoot
for ($i = 0; $i -lt 5; $i++) {
    $workspaceRoot = Split-Path $workspaceRoot -Parent
    if (Test-Path (Join-Path $workspaceRoot 'CLAUDE.md')) { break }
}

$logsDir = Join-Path $ProjectRoot 'out\logs'
$reportPath = Join-Path $logsDir 'scene_budget_report.json'
$summaryPath = Join-Path $logsDir 'scene_budget_summary.md'

# ---------------------------------------------------------------------------
# Initialize report
# ---------------------------------------------------------------------------
$report = New-SgdkArtifactEnvelope `
    -ToolName 'audit_scene_budget' `
    -ToolVersion $ToolVersion `
    -ProjectRoot $ProjectRoot `
    -WorkspaceRoot $workspaceRoot

$report['scenes'] = @()
$sceneResults = [System.Collections.ArrayList]::new()

# ---------------------------------------------------------------------------
# Load metrics
# ---------------------------------------------------------------------------
$metrics = $null
if (Test-Path -LiteralPath $RuntimeMetricsPath) {
    $metrics = Import-SceneBudgetMetrics -MetricsPath $RuntimeMetricsPath
}

# Also try to load from merged metrics
$mergedPath = Join-Path $ProjectRoot 'out\logs\merged_budget_metrics.json'
$mergedMetrics = $null
if (Test-Path -LiteralPath $mergedPath) {
    $mergedMetrics = Import-SceneBudgetMetrics -MetricsPath $mergedPath
}

# Also look at scene contracts for scene list
$contractPath = Join-Path $ProjectRoot 'doc\scene-contracts.json'
$contract = $null
if (Test-Path -LiteralPath $contractPath) {
    try {
        $contract = Get-Content -LiteralPath $contractPath -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch { $contract = $null }
}

# ---------------------------------------------------------------------------
# Build scene list and metrics
# ---------------------------------------------------------------------------
$scenesToAudit = @{}

# From contract
if ($contract -and $contract.PSObject.Properties['scenes']) {
    foreach ($s in $contract.scenes) {
        if ($s.PSObject.Properties['scene_id']) {
            $scenesToAudit[$s.scene_id] = @{ frames = @(); origin = 'inferred' }
        }
    }
}

# From runtime metrics (if they have scene-level data)
if ($metrics -and $metrics.PSObject.Properties['frame_metrics']) {
    foreach ($fm in $metrics.frame_metrics) {
        $sid = if ($fm.PSObject.Properties['scene_id']) { $fm.scene_id } else { 'unknown' }
        if (-not $scenesToAudit.ContainsKey($sid)) {
            $scenesToAudit[$sid] = @{ frames = @(); origin = 'measured' }
        }
        $scenesToAudit[$sid].frames += $fm
        $scenesToAudit[$sid].origin = 'measured'
    }
}

# Filter by SceneId if specified
if (-not [string]::IsNullOrWhiteSpace($SceneId)) {
    if ($scenesToAudit.ContainsKey($SceneId)) {
        $filtered = @{ $SceneId = $scenesToAudit[$SceneId] }
        $scenesToAudit = $filtered
    } else {
        # Create placeholder for requested scene
        $scenesToAudit = @{ $SceneId = @{ frames = @(); origin = 'inferred' } }
    }
}

# ---------------------------------------------------------------------------
# Audit each scene
# ---------------------------------------------------------------------------
if ($scenesToAudit.Count -eq 0) {
    # No scenes found — create inferred report from general metrics
    $report['status'] = 'warn'
    $report['failure_reason'] = 'No scene data available for budget audit'
    Write-SgdkJsonArtifact -Data $report -Path $reportPath | Out-Null
    Write-Host "[WARN]  No scene data available for audit"
    Write-Host "[INFO]  Report: $reportPath"
    exit 0
}

$hasErrors = $false

foreach ($sid in $scenesToAudit.Keys) {
    $sceneData = $scenesToAudit[$sid]
    $frames = @($sceneData.frames)
    $origin = $sceneData.origin

    if ($frames.Count -eq 0) {
        # No frame data — create inferred placeholder
        $r = [ordered]@{
            scene_id                  = $sid
            measurement_origin        = 'inferred'
            frames_analyzed           = 0
            dma_bytes_peak            = $null
            dma_ops_peak              = $null
            sprite_count_peak         = $null
            sprites_per_scanline_peak = $null
            pal_changes_peak          = $null
            vram_usage_estimate_peak  = $null
            cpu_overrun_count         = $null
            budget_status             = 'warn'
            budget_notes              = 'No frame metrics available. Budget cannot be evaluated.'
        }
        [void]$sceneResults.Add($r)
        continue
    }

    $budgetResult = Measure-SceneBudget -SceneId $sid -FrameMetrics $frames -MeasurementOrigin $origin
    [void]$sceneResults.Add($budgetResult)

    if ($budgetResult.budget_status -eq 'error') { $hasErrors = $true }
}

# ---------------------------------------------------------------------------
# Finalize
# ---------------------------------------------------------------------------
$report['scenes'] = @($sceneResults.ToArray())

if ($hasErrors) {
    if ($WarnOnly) {
        $report['status'] = 'warn'
        $report['failure_reason'] = 'Budget violations detected (downgraded to warning)'
    } else {
        $report['status'] = 'error'
        $report['failure_reason'] = 'Budget violations detected'
    }
} elseif (@($sceneResults | Where-Object { $_.budget_status -eq 'warn' }).Count -gt 0) {
    $report['status'] = 'warn'
    $report['failure_reason'] = 'Budget warnings present'
}

Write-SgdkJsonArtifact -Data $report -Path $reportPath | Out-Null
Write-SceneBudgetSummary -SceneResults @($sceneResults.ToArray()) -OutputPath $summaryPath

$okCount = @($sceneResults | Where-Object { $_.budget_status -eq 'ok' }).Count
$warnCount = @($sceneResults | Where-Object { $_.budget_status -eq 'warn' }).Count
$errCount = @($sceneResults | Where-Object { $_.budget_status -eq 'error' }).Count

Write-Host "[$($report['status'].ToString().ToUpper())] Budget audit: $($sceneResults.Count) scene(s) [OK:$okCount W:$warnCount E:$errCount]"
Write-Host "[INFO]  Report: $reportPath"
Write-Host "[INFO]  Summary: $summaryPath"

foreach ($s in $sceneResults) {
    $icon = switch ($s.budget_status) { 'ok' { 'OK' }; 'warn' { 'WARN' }; 'error' { 'ERR' }; default { '?' } }
    $origin = $s.measurement_origin
    $note = if ($s.budget_notes) { " - $($s.budget_notes)" } else { '' }
    Write-Host "  [$icon] $($s.scene_id) [$origin]$note"
}

if ($hasErrors -and -not $WarnOnly) { exit 1 }
exit 0
