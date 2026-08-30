<#
.SYNOPSIS
    Rejects archived skill aliases from active routing surfaces.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$AgentRoot = Join-Path $WrapperRoot ".agent"

$Archived = @(
    "level-manifest-architect",
    "color-conversion-curator",
    "dither-composite-transparency",
    "palette-cram-curator",
    "sprite-asset-budget-curator",
    "tilemap-attribute-director",
    "sfx-prep-fm-psg-pcm",
    "z80-audio-boundary-architect",
    "articulated-sprite-architect",
    "software-tile-rasterizer",
    "hscroll-linescroll-road-fx",
    "raster-palette-hint-director",
    "sprite-scanline-budgeter"
)

$ActiveSurfaces = @(
    (Join-Path $AgentRoot "framework_manifest.json"),
    (Join-Path $AgentRoot "pipelines"),
    (Join-Path $AgentRoot "workflows"),
    (Join-Path $AgentRoot "rules"),
    (Join-Path $AgentRoot "references\aaa_pipeline_curated_skill_map.json"),
    (Join-Path $AgentRoot "references\learning_owner_catalog.json")
)

$violations = New-Object System.Collections.Generic.List[object]
foreach ($surface in $ActiveSurfaces) {
    $files = @()
    if (Test-Path -LiteralPath $surface -PathType Leaf) {
        $files = @($surface)
    }
    elseif (Test-Path -LiteralPath $surface -PathType Container) {
        $files = @(Get-ChildItem -LiteralPath $surface -File -Recurse |
            Where-Object { $_.Extension -in @(".md", ".json", ".yaml") } |
            Select-Object -ExpandProperty FullName)
    }

    foreach ($file in $files) {
        $text = Get-Content -LiteralPath $file -Raw -Encoding UTF8
        foreach ($skillId in $Archived) {
            if ($text -match [regex]::Escape($skillId)) {
                $violations.Add([ordered]@{
                    skill_id = $skillId
                    file = $file
                })
            }
        }
    }
}

if ($violations.Count -gt 0) {
    $violations | ConvertTo-Json -Depth 4 | Write-Host
    throw "Archived skill aliases remain in active routing surfaces: $($violations.Count)"
}

$WorkspaceRoot = Split-Path (Split-Path $WrapperRoot -Parent) -Parent
$Bridge = Join-Path $WorkspaceRoot ".agents\skills"
$Legacy = Join-Path $AgentRoot "legacy\skills"
if (-not (Test-Path -LiteralPath $Bridge)) { throw "Codex skill bridge missing" }
if ((Get-Item -LiteralPath $Bridge -Force).Target -and
    ((Get-Item -LiteralPath $Bridge -Force).Target -match "legacy")) {
    throw "Codex skill bridge points to legacy"
}
$routeMap = Get-Content -LiteralPath (Join-Path $AgentRoot "references\aaa_pipeline_curated_skill_map.json") -Raw
if ($routeMap -notmatch "experimental_requires_benchmark") {
    throw "experimental raster route must require benchmark"
}
if ((Get-ChildItem -LiteralPath $Legacy -Recurse -Filter SKILL.md).Count -ne $Archived.Count) {
    throw "legacy skill count does not match archived alias set"
}

Write-Host "[PASS] active routes reference only active skill owners"
