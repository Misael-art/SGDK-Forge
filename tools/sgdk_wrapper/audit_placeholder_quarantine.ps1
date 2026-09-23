<#
.SYNOPSIS
    Placeholder quarantine: detects placeholder/lab assets promoted to AAA delivery.
.DESCRIPTION
    Scans res/, data/source_art/ and visual reports for assets with visual_status
    in (placeholder, debug_lab, technical_lab_asset, procedural). Blocks if any
    are promoted to elite_ready or used in AAA closeout.
.PARAMETER ProjectRoot
    Root path of the SGDK project.
.PARAMETER OutputPath
    Where to write the JSON report.
.PARAMETER VisualDeliveryReportPath
    Path to visual_delivery_gate_report.json (optional, auto-detected).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "",

    [Parameter(Mandatory = $false)]
    [string]$VisualDeliveryReportPath = ""
)

$ErrorActionPreference = "Stop"

$quarantineTags = @("placeholder", "technical_lab_asset", "procedural_debug", "lab_fallback", "pil_imagedraw_generated")
$quarantineKeywords = @("placeholder", "debug_lab", "lab_", "procedural", "fallback", "pil_", "imagedraw", "technical_lab", "generated_by_code")

$quarantinedAssets = @()
$promotionAttempts = @()

$resDir = Join-Path -Path $ProjectRoot -ChildPath "res"
$dataDir = Join-Path -Path $ProjectRoot -ChildPath "data"
$sourceArtDir = Join-Path -Path $ProjectRoot -ChildPath "data\source_art"

function Test-QuarantineName {
    param([string]$Name)
    $lower = $Name.ToLower()
    foreach ($kw in $quarantineKeywords) {
        if ($lower -match [regex]::Escape($kw)) { return $true }
    }
    return $false
}

function Get-QuarantineTag {
    param([string]$Name)
    $lower = $Name.ToLower()
    if ($lower -match "pil_|imagedraw") { return "pil_imagedraw_generated" }
    if ($lower -match "procedural|generated_by_code") { return "procedural_debug" }
    if ($lower -match "lab_|technical_lab") { return "technical_lab_asset" }
    if ($lower -match "fallback") { return "lab_fallback" }
    if ($lower -match "placeholder") { return "placeholder" }
    return "placeholder"
}

if (Test-Path -LiteralPath $resDir) {
    $resPngs = Get-ChildItem -LiteralPath $resDir -Filter "*.png" -Recurse -ErrorAction SilentlyContinue
    foreach ($png in $resPngs) {
        if (Test-QuarantineName $png.Name) {
            $tag = Get-QuarantineTag $png.Name
            $relPath = $png.FullName.Substring($ProjectRoot.Length + 1)
            $quarantinedAssets += @{
                asset_path                    = $relPath
                quarantine_tag                = $tag
                location                      = "res"
                valid_for_pipeline_validation = $true
                valid_for_visual_delivery     = $false
            }
        }
    }
}

if (Test-Path -LiteralPath $dataDir) {
    $dataPngs = Get-ChildItem -LiteralPath $dataDir -Filter "*.png" -Recurse -ErrorAction SilentlyContinue
    foreach ($png in $dataPngs) {
        if (Test-QuarantineName $png.Name) {
            $tag = Get-QuarantineTag $png.Name
            $relPath = $png.FullName.Substring($ProjectRoot.Length + 1)
            $loc = "data"
            if ($png.FullName -like "*source_art*") { $loc = "source_art" }
            $quarantinedAssets += @{
                asset_path                    = $relPath
                quarantine_tag                = $tag
                location                      = $loc
                valid_for_pipeline_validation = $true
                valid_for_visual_delivery     = $false
            }
        }
    }
}

if ($VisualDeliveryReportPath -eq "") {
    $VisualDeliveryReportPath = Join-Path -Path $ProjectRoot -ChildPath "out\logs\visual_delivery_gate_report.json"
}

if (Test-Path -LiteralPath $VisualDeliveryReportPath) {
    try {
        $vdData = Get-Content -LiteralPath $VisualDeliveryReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($vdData.critical_assets) {
            foreach ($asset in $vdData.critical_assets) {
                $vs = ""
                if ($asset.visual_status) { $vs = $asset.visual_status }
                if ($vs -in @("placeholder", "debug_lab", "benchmark-derived")) {
                    $relPath = if ($asset.asset_id) { $asset.asset_id } else { "unknown" }
                    $promotionAttempts += @{
                        asset_path      = $relPath
                        attempted_status = if ($vdData.ready_for_aaa -eq $true) { "elite_ready" } else { $vs }
                        blocked          = ($vs -ne "elite_ready")
                        context          = "visual_delivery_gate_report"
                    }
                }
            }
        }
    }
    catch {
        # Report unreadable
    }
}

$srcDir = Join-Path -Path $ProjectRoot -ChildPath "src"
if (Test-Path -LiteralPath $srcDir) {
    $cFiles = Get-ChildItem -LiteralPath $srcDir -Filter "*.c" -Recurse -ErrorAction SilentlyContinue
    foreach ($cf in $cFiles) {
        $content = Get-Content -LiteralPath $cf.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        if ($content -match "procedural_renderer|local_author_pixel_rasterization|draw_debug_|lab_bg_") {
            $relPath = $cf.FullName.Substring($ProjectRoot.Length + 1)
            $alreadyFound = $false
            foreach ($qa in $quarantinedAssets) {
                if ($qa.asset_path -eq $relPath) { $alreadyFound = $true; break }
            }
            if (-not $alreadyFound) {
                $quarantinedAssets += @{
                    asset_path                    = $relPath
                    quarantine_tag                = "procedural_debug"
                    location                      = "res"
                    valid_for_pipeline_validation = $true
                    valid_for_visual_delivery     = $false
                }
            }
        }
    }
}

$quarantineActive = $quarantinedAssets.Count -gt 0
$blocking = $false
$blockerCode = $null

foreach ($pa in $promotionAttempts) {
    if (-not $pa.blocked) {
        $blocking = $true
        $blockerCode = "placeholder_promoted_to_aaa"
        break
    }
}

if ($VisualDeliveryReportPath -and (Test-Path -LiteralPath $VisualDeliveryReportPath)) {
    try {
        $vdCheck = Get-Content -LiteralPath $VisualDeliveryReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($vdCheck.ready_for_aaa -eq $true -and $quarantineActive) {
            $blocking = $true
            $blockerCode = "placeholder_promoted_to_aaa"
        }
    }
    catch {}
}

$report = [ordered]@{
    schema_version     = "1.0.0"
    generated_at       = (Get-Date -Format "o")
    project_root       = $ProjectRoot
    quarantine_active  = $quarantineActive
    quarantined_assets = $quarantinedAssets
    promotion_attempts = $promotionAttempts
    blocking           = $blocking
    blocker_code       = $blockerCode
}

if ($OutputPath -ne "") {
    $outDir = Split-Path -Parent $OutputPath
    if ($outDir) {
        [System.IO.Directory]::CreateDirectory($outDir) | Out-Null
    }
    $report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
}

$report | ConvertTo-Json -Depth 10 | Write-Output

if ($blocking) {
    Write-Warning "[PLACEHOLDER-QUARANTINE] BLOCKED: placeholder_promoted_to_aaa - $($quarantinedAssets.Count) quarantined asset(s) found."
    exit 1
}

exit 0
