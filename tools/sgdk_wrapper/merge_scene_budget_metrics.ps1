<#
.SYNOPSIS
    Merges multiple metric sources into a unified scene budget metrics file.
.DESCRIPTION
    Standalone script that combines runtime_metrics.json and scene regression
    artifacts into a consolidated metrics dataset for the budget auditor.

    This script does NOT modify any existing wrapper behavior.
    It writes only to out/logs/.
.PARAMETER ProjectRoot
    Absolute path to the project root directory.
.PARAMETER SourcePaths
    Array of absolute paths to metric JSON files to merge.
    Defaults to auto-discovery of runtime_metrics.json and regression evidence.
.PARAMETER OutputPath
    Absolute path for the merged output. Defaults to <ProjectRoot>/out/logs/merged_budget_metrics.json.
.EXAMPLE
    .\merge_scene_budget_metrics.ps1 -ProjectRoot "C:\Projects\MyGame"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ProjectRoot,
    [string[]]$SourcePaths,
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Import modules
# ---------------------------------------------------------------------------
$libDir = Join-Path $PSScriptRoot 'lib'
Import-Module (Join-Path $libDir 'sgdk_artifact_contracts.psm1') -Force

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot -ErrorAction Stop).Path

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $ProjectRoot 'out\logs\merged_budget_metrics.json'
}

# Auto-discover sources if not provided
if (-not $SourcePaths -or $SourcePaths.Count -eq 0) {
    $discovered = @()

    # runtime_metrics.json
    $rtMetrics = Join-Path $ProjectRoot 'out\logs\runtime_metrics.json'
    if (Test-Path -LiteralPath $rtMetrics) { $discovered += $rtMetrics }

    # Scene evidence bundles
    $scenesDir = Join-Path $ProjectRoot 'out\evidence\scenes'
    if (Test-Path -LiteralPath $scenesDir) {
        $bundles = Get-ChildItem -Path $scenesDir -Filter 'bundle.json' -Recurse -ErrorAction SilentlyContinue
        foreach ($b in $bundles) { $discovered += $b.FullName }
    }

    $SourcePaths = $discovered
}

# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------
$mergedScenes = @{}

foreach ($sourcePath in $SourcePaths) {
    if (-not (Test-Path -LiteralPath $sourcePath)) {
        Write-Warning "Source not found, skipping: $sourcePath"
        continue
    }

    try {
        $data = Get-Content -LiteralPath $sourcePath -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        Write-Warning "Invalid JSON in $sourcePath, skipping"
        continue
    }

    # Handle different source formats
    if ($data.PSObject.Properties['scenes']) {
        # Budget or regression report with scenes array
        foreach ($scene in $data.scenes) {
            $sid = if ($scene.PSObject.Properties['scene_id']) { $scene.scene_id } else { continue }
            if (-not $mergedScenes.ContainsKey($sid)) {
                $mergedScenes[$sid] = @{ frames = @(); origin = 'estimated' }
            }
            if ($scene.PSObject.Properties['measurement_origin']) {
                $mergedScenes[$sid].origin = $scene.measurement_origin
            }
        }
    } elseif ($data.PSObject.Properties['scene_id']) {
        # Single scene evidence bundle
        $sid = $data.scene_id
        if (-not $mergedScenes.ContainsKey($sid)) {
            $mergedScenes[$sid] = @{ frames = @(); origin = 'inferred' }
        }
    } elseif ($data.PSObject.Properties['frame_metrics']) {
        # Runtime metrics with frame data
        foreach ($fm in $data.frame_metrics) {
            $sid = if ($fm.PSObject.Properties['scene_id']) { $fm.scene_id } else { 'unknown' }
            if (-not $mergedScenes.ContainsKey($sid)) {
                $mergedScenes[$sid] = @{ frames = @(); origin = 'measured' }
            }
            $mergedScenes[$sid].frames += $fm
        }
    }
}

# ---------------------------------------------------------------------------
# Write merged output
# ---------------------------------------------------------------------------
$workspaceRoot = $PSScriptRoot
for ($i = 0; $i -lt 5; $i++) {
    $workspaceRoot = Split-Path $workspaceRoot -Parent
    if (Test-Path (Join-Path $workspaceRoot 'CLAUDE.md')) { break }
}

$output = New-SgdkArtifactEnvelope `
    -ToolName 'merge_scene_budget_metrics' `
    -ToolVersion '0.1.0' `
    -ProjectRoot $ProjectRoot `
    -WorkspaceRoot $workspaceRoot

$output['sources_count'] = $SourcePaths.Count
$output['scenes_count'] = $mergedScenes.Count
$output['scenes'] = @{}

foreach ($sid in $mergedScenes.Keys) {
    $output['scenes'][$sid] = [ordered]@{
        scene_id           = $sid
        measurement_origin = $mergedScenes[$sid].origin
        frames_count       = $mergedScenes[$sid].frames.Count
        source_files       = @($SourcePaths | ForEach-Object { Split-Path $_ -Leaf })
    }
}

Write-SgdkJsonArtifact -Data $output -Path $OutputPath | Out-Null

Write-Host "[OK]    Merged $($SourcePaths.Count) source(s) into $($mergedScenes.Count) scene(s)"
Write-Host "[INFO]  Output: $OutputPath"
exit 0
