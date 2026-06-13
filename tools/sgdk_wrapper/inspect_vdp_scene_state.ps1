<#
.SYNOPSIS
    Inspects VDP state for a scene from a dump file and produces a structured report.
.DESCRIPTION
    Standalone script for the AAA agent ecosystem. Reads a VDP dump binary,
    analyzes palettes, tiles, sprites, and produces vdp_inspection.json.

    This script does NOT modify any existing wrapper behavior.
    It writes only to out/logs/ and out/evidence/vdp/.

    DECISION PENDING: VDP dump format from BlastEm is not yet canonical.
    This script uses a best-effort parser for raw VRAM (+ optional CRAM).
.PARAMETER ProjectRoot
    Absolute path to the project root directory.
.PARAMETER SceneId
    Scene identifier for this inspection.
.PARAMETER VdpDumpPath
    Absolute path to the VDP dump binary. Defaults to out/evidence/blastem/visual_vdp_dump.bin.
.PARAMETER OutputPath
    Absolute path for the inspection JSON. Defaults to out/logs/vdp_inspection.json.
.PARAMETER WarnOnly
    If set, failures produce warnings instead of error exit codes.
.EXAMPLE
    .\inspect_vdp_scene_state.ps1 -ProjectRoot "C:\Projects\MyGame" -SceneId gameplay_stage1
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$ProjectRoot,
    [Parameter(Mandatory)][string]$SceneId,
    [string]$VdpDumpPath,
    [string]$OutputPath,
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
Import-Module (Join-Path $libDir 'vdp_inspection.psm1') -Force

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot -ErrorAction Stop).Path

if ([string]::IsNullOrWhiteSpace($VdpDumpPath)) {
    $VdpDumpPath = Join-Path $ProjectRoot 'out\evidence\blastem\visual_vdp_dump.bin'
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $ProjectRoot 'out\logs\vdp_inspection.json'
}

$workspaceRoot = $PSScriptRoot
for ($i = 0; $i -lt 5; $i++) {
    $workspaceRoot = Split-Path $workspaceRoot -Parent
    if (Test-Path (Join-Path $workspaceRoot 'CLAUDE.md')) { break }
}

# ---------------------------------------------------------------------------
# Initialize report
# ---------------------------------------------------------------------------
$report = New-SgdkArtifactEnvelope `
    -ToolName 'inspect_vdp_scene_state' `
    -ToolVersion $ToolVersion `
    -ProjectRoot $ProjectRoot `
    -WorkspaceRoot $workspaceRoot

$report['scene_id'] = $SceneId
$report['vdp_dump_path'] = $VdpDumpPath
$report['inspection_status'] = 'error'

# ---------------------------------------------------------------------------
# Load VDP dump
# ---------------------------------------------------------------------------
$dump = Import-VdpDump -DumpPath $VdpDumpPath

if (-not $dump.Valid) {
    $reason = if ($dump.Error) { $dump.Error } else { "VDP dump invalid or too small (got $($dump.FileSize) bytes, need >= 65536)" }
    Set-SgdkArtifactFailure -Artifact $report -Reason $reason -Warn:$WarnOnly
    $report['inspection_status'] = 'error'
    Write-SgdkJsonArtifact -Data $report -Path $OutputPath | Out-Null
    Write-Host "[$(if ($WarnOnly) {'WARN'} else {'ERROR'})] $reason"
    Write-Host "[INFO]  Report: $OutputPath"
    if ($WarnOnly) { exit 0 } else { exit 1 }
}

Write-Host "[INFO]  VDP dump loaded: $($dump.FileSize) bytes"

# ---------------------------------------------------------------------------
# Analyze components
# ---------------------------------------------------------------------------
$paletteData = Measure-VdpPaletteUsage -Cram $dump.Cram
$tileData = Measure-VdpTileUsage -Vram $dump.Vram
$spriteData = Measure-VdpSpriteState -Vram $dump.Vram

$inspection = New-VdpInspectionArtifact `
    -SceneId $SceneId `
    -PaletteData $paletteData `
    -TileData $tileData `
    -SpriteData $spriteData

# ---------------------------------------------------------------------------
# Merge into report
# ---------------------------------------------------------------------------
foreach ($key in $inspection.Keys) {
    $report[$key] = $inspection[$key]
}

Write-SgdkJsonArtifact -Data $report -Path $OutputPath | Out-Null

# Summary
$status = $report['inspection_status']
Write-Host "[$($status.ToString().ToUpper())] VDP inspection for '$SceneId'"
Write-Host "  Tiles: $($tileData.used_tiles)/$($tileData.total_tiles) ($([math]::Round($tileData.usage_fraction * 100, 1))%) [$($tileData.unique_tiles) unique, $($tileData.duplicate_tiles) duplicate]"
Write-Host "  Sprites: $($spriteData.sprite_count)/80 [max $($spriteData.max_sprites_per_scanline)/scanline]"

$totalUniqueColors = 0
foreach ($pal in $paletteData.palettes) {
    $totalUniqueColors += $pal.unique_colors
}
Write-Host "  Palette: $totalUniqueColors unique colors across 4 palettes"

if ($inspection.inspection_notes) {
    Write-Host "  Notes: $($inspection.inspection_notes)"
}
Write-Host "[INFO]  Report: $OutputPath"

exit 0
