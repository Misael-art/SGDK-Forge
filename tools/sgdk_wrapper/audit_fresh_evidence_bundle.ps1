<#
.SYNOPSIS
    Revalidates a sealed same-session emulator bundle before closeout.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ProjectRoot,
    [Parameter(Mandatory = $false)][string]$ManifestPath = "",
    [Parameter(Mandatory = $false)][string]$OutputPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
if ([string]::IsNullOrWhiteSpace($ManifestPath)) {
    $ManifestPath = Join-Path $ProjectRoot "out\evidence\blastem\evidence_manifest.json"
}
$ManifestPath = [System.IO.Path]::GetFullPath($ManifestPath)
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $ProjectRoot "out\logs\fresh_evidence_bundle_audit_report.json"
}
$OutputPath = [System.IO.Path]::GetFullPath($OutputPath)
$blockers = New-Object System.Collections.Generic.List[string]
$artifacts = New-Object System.Collections.Generic.List[object]
$manifest = $null
$manifestRoot = Split-Path $ManifestPath -Parent
$projectRom = Join-Path $ProjectRoot "out\rom.bin"

if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
    $blockers.Add("fresh_evidence_manifest_missing")
} else {
    try {
        $manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        $blockers.Add("fresh_evidence_manifest_unreadable")
    }
}

if ($manifest) {
    $sessionId = [string]$manifest.session_id
    $romSha = ([string]$manifest.rom_sha256).ToLowerInvariant()
    if ([string]$manifest.status -ne "sealed") { $blockers.Add("fresh_evidence_manifest_not_sealed") }
    if (@($manifest.blockers).Count -gt 0) { $blockers.Add("fresh_evidence_manifest_has_blockers") }
    if (-not [bool]$manifest.semantic_capture_valid) { $blockers.Add("fresh_evidence_semantic_capture_invalid") }
    if ([string]::IsNullOrWhiteSpace($sessionId)) { $blockers.Add("fresh_evidence_session_missing") }
    if ($romSha -notmatch '^[0-9a-f]{64}$') { $blockers.Add("fresh_evidence_rom_identity_missing") }

    $expectedNames = @("rom", "screenshot", "sram", "vdp_dump", "runtime_metrics")
    foreach ($expectedName in $expectedNames) {
        if (@($manifest.artifacts | Where-Object { [string]$_.name -eq $expectedName }).Count -ne 1) {
            $blockers.Add("fresh_evidence_artifact_cardinality:$expectedName")
        }
    }
    foreach ($artifact in @($manifest.artifacts)) {
        $artifactPath = Join-Path $manifestRoot ([string]$artifact.path)
        $actualHash = $null
        if (-not (Test-Path -LiteralPath $artifactPath -PathType Leaf)) {
            $blockers.Add("fresh_evidence_artifact_missing:$($artifact.name)")
        } else {
            $actualHash = (Get-FileHash -LiteralPath $artifactPath -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($actualHash -ne ([string]$artifact.sha256).ToLowerInvariant()) {
                $blockers.Add("fresh_evidence_artifact_hash_mismatch:$($artifact.name)")
            }
        }
        if ([string]$artifact.session_id -ne $sessionId) {
            $blockers.Add("fresh_evidence_session_mismatch:$($artifact.name)")
        }
        if (([string]$artifact.rom_sha256).ToLowerInvariant() -ne $romSha) {
            $blockers.Add("fresh_evidence_artifact_rom_mismatch:$($artifact.name)")
        }
        $artifacts.Add([ordered]@{ name = [string]$artifact.name; path = $artifactPath; actual_sha256 = $actualHash })
    }

    if (-not (Test-Path -LiteralPath $projectRom -PathType Leaf)) {
        $blockers.Add("fresh_evidence_current_rom_missing")
    } elseif ((Get-FileHash -LiteralPath $projectRom -Algorithm SHA256).Hash.ToLowerInvariant() -ne $romSha) {
        $blockers.Add("fresh_evidence_current_rom_mismatch")
    }

    $freshnessPath = Join-Path $manifestRoot "freshness_report.json"
    if (-not (Test-Path -LiteralPath $freshnessPath -PathType Leaf)) {
        $blockers.Add("fresh_evidence_freshness_report_missing")
    } else {
        try {
            $freshness = Get-Content -LiteralPath $freshnessPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ([string]$freshness.status -ne "ok") { $blockers.Add("fresh_evidence_freshness_blocked") }
            if ([string]$freshness.session_id -ne $sessionId) { $blockers.Add("fresh_evidence_freshness_session_mismatch") }
            if (([string]$freshness.rom_sha256).ToLowerInvariant() -ne $romSha) { $blockers.Add("fresh_evidence_freshness_rom_mismatch") }
        } catch {
            $blockers.Add("fresh_evidence_freshness_report_unreadable")
        }
    }
}

$uniqueBlockers = @($blockers | Select-Object -Unique)
$ok = $uniqueBlockers.Count -eq 0
$report = [ordered]@{
    schema_version = "1.0.0"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    tool_name = "audit_fresh_evidence_bundle"
    tool_version = "1.0.0"
    status = if ($ok) { "ok" } else { "blocked" }
    project_root = $ProjectRoot
    manifest_path = $ManifestPath
    session_id = if ($manifest) { [string]$manifest.session_id } else { $null }
    rom_sha256 = if ($manifest) { [string]$manifest.rom_sha256 } else { $null }
    artifacts = [object[]]$artifacts.ToArray()
    blockers = $uniqueBlockers
}
$outputDir = Split-Path $OutputPath -Parent
if (-not (Test-Path -LiteralPath $outputDir -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
Write-Host ("[FRESH-EVIDENCE] status={0} blockers={1} report={2}" -f $report.status, $uniqueBlockers.Count, $OutputPath)
if (-not $ok) { exit 1 }
exit 0
