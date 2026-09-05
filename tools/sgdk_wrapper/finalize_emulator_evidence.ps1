<#
.SYNOPSIS
    Seals emulator evidence against the current ROM identity.
.DESCRIPTION
    Reads the captured emulator session, hashes the current ROM and writes an
    immutable closeout decision. A rebuild after capture makes the seal fail.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $false)]
    [string]$RomPath = "",

    [Parameter(Mandatory = $false)]
    [string]$EvidencePath = "",

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "",

    [Parameter(Mandatory = $false)]
    [switch]$WarnOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
if ([string]::IsNullOrWhiteSpace($RomPath)) {
    $RomPath = Join-Path $ProjectRoot "out\rom.bin"
}
if ([string]::IsNullOrWhiteSpace($EvidencePath)) {
    $EvidencePath = Join-Path $ProjectRoot "out\logs\emulator_session.json"
}
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $ProjectRoot "out\logs\evidence_closeout_report.json"
}

$blockerCode = $null
$failureReason = $null
$capturedHash = $null
$currentHash = $null
$evidenceFiles = @()
$evidenceArtifacts = @()
$missingEvidenceFiles = @()
$evidence = $null
$semanticScreenshotPath = $null
$semanticCaptureReportPath = Join-Path $ProjectRoot "out\logs\screenshot_semantic_gate_report.json"
$semanticCaptureReport = $null
$semanticCaptureValid = $null

if (-not (Test-Path -LiteralPath $RomPath -PathType Leaf)) {
    $blockerCode = "rom_missing_for_evidence_closeout"
    $failureReason = "Current ROM was not found."
}
elseif (-not (Test-Path -LiteralPath $EvidencePath -PathType Leaf)) {
    $blockerCode = "emulator_evidence_missing"
    $failureReason = "Emulator evidence report was not found."
}
else {
    try {
        $evidence = Get-Content -LiteralPath $EvidencePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $capturedHash = [string]$evidence.rom_sha256
        $currentHash = (Get-FileHash -LiteralPath $RomPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($capturedHash) {
            $capturedHash = $capturedHash.ToLowerInvariant()
        }

        if ($evidence.PSObject.Properties.Name -contains "evidence_files") {
            $evidenceFiles += @($evidence.evidence_files)
        }
        foreach ($propertyName in @("screenshot_path", "save_sram_path", "sram_path", "vdp_dump_path", "visual_vdp_dump_path")) {
            if ($evidence.PSObject.Properties.Name -contains $propertyName) {
                $value = [string]$evidence.$propertyName
                if (-not [string]::IsNullOrWhiteSpace($value)) {
                    $evidenceFiles += $value
                }
            }
        }
        $evidenceFiles = @($evidenceFiles | Where-Object { $_ } | Select-Object -Unique)
        foreach ($evidenceFile in $evidenceFiles) {
            $resolvedEvidencePath = [string]$evidenceFile
            if (-not [System.IO.Path]::IsPathRooted($resolvedEvidencePath)) {
                $resolvedEvidencePath = Join-Path $ProjectRoot $resolvedEvidencePath
            }
            $resolvedEvidencePath = [System.IO.Path]::GetFullPath($resolvedEvidencePath)
            if (-not (Test-Path -LiteralPath $resolvedEvidencePath -PathType Leaf)) {
                $missingEvidenceFiles += $resolvedEvidencePath
                continue
            }
            if (-not $semanticScreenshotPath -and [System.IO.Path]::GetExtension($resolvedEvidencePath).ToLowerInvariant() -eq ".png") {
                $semanticScreenshotPath = $resolvedEvidencePath
            }
            $fileInfo = Get-Item -LiteralPath $resolvedEvidencePath
            $evidenceArtifacts += [ordered]@{
                path = $resolvedEvidencePath
                size_bytes = [long]$fileInfo.Length
                sha256 = (Get-FileHash -LiteralPath $resolvedEvidencePath -Algorithm SHA256).Hash.ToLowerInvariant()
            }
        }

        if ($semanticScreenshotPath) {
            $semanticAuditScript = Join-Path $PSScriptRoot "audit_screenshot_semantics.ps1"
            $currentPowerShellHost = (Get-Process -Id $PID).Path
            & $currentPowerShellHost -NoProfile -ExecutionPolicy Bypass -File $semanticAuditScript `
                -ProjectRoot $ProjectRoot `
                -ScreenshotPath $semanticScreenshotPath `
                -OutputPath $semanticCaptureReportPath `
                -RomPath $RomPath `
                -EvidenceSessionId $(if ($evidence.PSObject.Properties.Name -contains "session_id" -and $evidence.session_id) { [string]$evidence.session_id } else { "" }) `
                -WarnOnly | Out-Host
            if (Test-Path -LiteralPath $semanticCaptureReportPath -PathType Leaf) {
                try {
                    $semanticCaptureReport = Get-Content -LiteralPath $semanticCaptureReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
                    $semanticCaptureValid = [bool]$semanticCaptureReport.semantic_capture_valid
                } catch {
                    $semanticCaptureValid = $false
                }
            } else {
                $semanticCaptureValid = $false
            }
        }

        if ([string]::IsNullOrWhiteSpace($capturedHash)) {
            $blockerCode = "captured_rom_identity_missing"
            $failureReason = "Evidence does not declare rom_sha256."
        }
        elseif ($capturedHash -ne $currentHash) {
            $blockerCode = "rom_identity_changed_after_capture"
            $failureReason = "Current ROM hash differs from the captured ROM hash."
        }
        elseif (($evidence.PSObject.Properties.Name -contains "evidence_stale") -and [bool]$evidence.evidence_stale) {
            $blockerCode = "emulator_evidence_stale"
            $failureReason = if ($evidence.stale_reason) { [string]$evidence.stale_reason } else { "Evidence report is marked stale." }
        }
        elseif ($evidenceFiles.Count -eq 0) {
            $blockerCode = "emulator_evidence_files_missing"
            $failureReason = "Evidence report contains no captured artifact paths."
        }
        elseif ($missingEvidenceFiles.Count -gt 0) {
            $blockerCode = "emulator_evidence_artifact_missing"
            $failureReason = "One or more captured evidence artifacts no longer exist."
        }
        elseif ($semanticScreenshotPath -and -not [bool]$semanticCaptureValid) {
            $blockerCode = if ($semanticCaptureReport -and $semanticCaptureReport.blocker_code) { [string]$semanticCaptureReport.blocker_code } else { "screenshot_semantic_gate_unavailable" }
            $failureReason = if ($semanticCaptureReport -and $semanticCaptureReport.failure_reason) { [string]$semanticCaptureReport.failure_reason } else { "Screenshot semantic integrity could not be proven." }
        }
    }
    catch {
        $blockerCode = "emulator_evidence_unreadable"
        $failureReason = $_.Exception.Message
    }
}

$sealed = [string]::IsNullOrWhiteSpace([string]$blockerCode)
$report = [ordered]@{
    schema_version = "1.0.0"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    tool_name = "finalize_emulator_evidence"
    tool_version = "1.1.0"
    project_root = $ProjectRoot
    status = if ($sealed) { "ok" } elseif ($WarnOnly) { "warn" } else { "error" }
    seal_status = if ($sealed) { "sealed" } else { "rejected" }
    blocker_code = $blockerCode
    failure_reason = $failureReason
    rom_path = $RomPath
    evidence_path = $EvidencePath
    captured_rom_sha256 = $capturedHash
    current_rom_sha256 = $currentHash
    rom_identity_stable = $sealed
    evidence_files = @($evidenceFiles)
    evidence_artifacts = @($evidenceArtifacts)
    missing_evidence_files = @($missingEvidenceFiles)
    semantic_capture_report_path = if (Test-Path -LiteralPath $semanticCaptureReportPath -PathType Leaf) { $semanticCaptureReportPath } else { $null }
    semantic_capture_valid = $semanticCaptureValid
    semantic_capture_claim_impacts = if ($semanticCaptureReport) { $semanticCaptureReport.claim_impacts } else { $null }
    freeze_then_capture_contract = [ordered]@{
        build_before_capture = $true
        rebuild_after_capture_allowed = $false
        reports_may_follow_capture = $true
    }
}

$outputDir = Split-Path -Parent $OutputPath
if ($outputDir) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
Write-Host ("[EVIDENCE-SEAL] status={0} seal={1} report={2}" -f $report.status, $report.seal_status, $OutputPath)

if (-not $sealed -and -not $WarnOnly) { exit 1 }
exit 0
