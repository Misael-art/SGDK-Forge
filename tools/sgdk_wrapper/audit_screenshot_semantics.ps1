<#
.SYNOPSIS
    Runs the canonical semantic integrity gate for an emulator screenshot.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectRoot = "",

    [Parameter(Mandatory = $false)]
    [string]$ScreenshotPath = "",

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "",

    [Parameter(Mandatory = $false)]
    [string]$RomPath = "",

    [Parameter(Mandatory = $false)]
    [string]$EvidenceSessionId = "",

    [Parameter(Mandatory = $false)]
    [switch]$WarnOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "_lib\sgdk_common.ps1")

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = (Get-Location).Path
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
if ([string]::IsNullOrWhiteSpace($ScreenshotPath)) {
    $ScreenshotPath = Join-Path $ProjectRoot "out\evidence\blastem\screenshot.png"
}
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $ProjectRoot "out\logs\screenshot_semantic_gate_report.json"
}
if ([string]::IsNullOrWhiteSpace($RomPath)) {
    $RomPath = Join-Path $ProjectRoot "out\rom.bin"
}
if ([string]::IsNullOrWhiteSpace($EvidenceSessionId)) {
    $sessionPath = Join-Path $ProjectRoot "out\logs\emulator_session.json"
    if (Test-Path -LiteralPath $sessionPath -PathType Leaf) {
        try {
            $sessionData = Get-Content -LiteralPath $sessionPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($sessionData.session_id) { $EvidenceSessionId = [string]$sessionData.session_id }
        } catch {
        }
    }
}

$analyzerPath = Join-Path $PSScriptRoot "screenshot_semantic_gate.py"
$pythonPath = SGDK_GetPythonPath
$exitCode = 2

if ($pythonPath -and (Test-Path -LiteralPath $analyzerPath -PathType Leaf)) {
    $analyzerArgs = @($analyzerPath, "--path", $ScreenshotPath, "--output", $OutputPath, "--rom-path", $RomPath)
    if (-not [string]::IsNullOrWhiteSpace($EvidenceSessionId)) {
        $analyzerArgs += @("--session-id", $EvidenceSessionId)
    }
    & $pythonPath @analyzerArgs
    $exitCode = $LASTEXITCODE
} else {
    $screenshotHash = $null
    if (Test-Path -LiteralPath $ScreenshotPath -PathType Leaf) {
        $screenshotHash = (Get-FileHash -LiteralPath $ScreenshotPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    $fallbackReport = [ordered]@{
        schema_version = "1.0.0"
        generated_at = (Get-Date).ToUniversalTime().ToString("o")
        tool_name = "screenshot_semantic_gate"
        tool_version = "1.0.0"
        screenshot_path = [System.IO.Path]::GetFullPath($ScreenshotPath)
        screenshot_sha256 = $screenshotHash
        rom_sha256 = if (Test-Path -LiteralPath $RomPath -PathType Leaf) { (Get-FileHash -LiteralPath $RomPath -Algorithm SHA256).Hash.ToLowerInvariant() } else { $null }
        evidence_session_id = if ($EvidenceSessionId) { $EvidenceSessionId } else { $null }
        status = "error"
        decision = "error"
        semantic_capture_valid = $false
        blocker_code = "screenshot_semantic_gate_unavailable"
        failure_reason = if (-not $pythonPath) { "Python is unavailable." } else { "Canonical analyzer is unavailable." }
        width = $null
        height = $null
        dominant_ratio = $null
        edge_density = $null
        metrics = [ordered]@{
            dominant_color_rgb = $null
            luminance_variance = $null
            unique_colors = $null
            sampled_pixels = $null
            edge_pairs = $null
        }
        thresholds = [ordered]@{
            edge_color_delta = 48
            minimum_edge_density = 0.04
            maximum_dominant_ratio = 0.985
            minimum_luminance_variance = 1.0
        }
        reasons = @("semantic_gate_dependency_missing")
        claim_impacts = [ordered]@{
            visual = "unproven"
            gameplay = "unproven"
            performance = "unproven"
        }
    }
    $outputDir = Split-Path -Parent $OutputPath
    if ($outputDir) {
        New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
    }
    $fallbackReport | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
}

$reportStatus = "error"
$blockerCode = "screenshot_semantic_gate_unavailable"
if (Test-Path -LiteralPath $OutputPath -PathType Leaf) {
    try {
        $report = Get-Content -LiteralPath $OutputPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $reportStatus = [string]$report.status
        $blockerCode = [string]$report.blocker_code
    } catch {
        $exitCode = 2
    }
}

Write-Host ("[SCREENSHOT-SEMANTIC] status={0} blocker={1} report={2}" -f $reportStatus, $blockerCode, $OutputPath)
if ($exitCode -ne 0 -and -not $WarnOnly) { exit 1 }
exit 0
