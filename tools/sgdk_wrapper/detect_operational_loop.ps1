<#
.SYNOPSIS
    Detects operational loops: same blockers in 3 consecutive builds.
.DESCRIPTION
    Reads recent validation reports and checks if the same blocking statuses
    appear in 3 or more consecutive builds. If detected, blocks new builds
    until a documented strategic decision is made.
.PARAMETER ProjectRoot
    Root path of the SGDK project.
.PARAMETER OutputPath
    Where to write the JSON report.
.PARAMETER Threshold
    Number of consecutive builds with same blockers to trigger loop (default: 3).
.PARAMETER ValidationReportDir
    Directory containing validation reports (default: out/logs).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "",

    [Parameter(Mandatory = $false)]
    [int]$Threshold = 3,

    [Parameter(Mandatory = $false)]
    [int]$WarningThreshold = 2,

    [Parameter(Mandatory = $false)]
    [string]$ValidationReportDir = ""
)

$ErrorActionPreference = "Stop"

if ($ValidationReportDir -eq "") {
    $ValidationReportDir = Join-Path -Path $ProjectRoot -ChildPath "out\logs"
}

$buildsAnalyzed = @()
$reportFiles = @()
$buildMetaFiles = @(
    Get-ChildItem -LiteralPath (Join-Path $ProjectRoot "doc\changelog\roms") `
        -Filter "build_meta.json" `
        -Recurse `
        -File `
        -ErrorAction SilentlyContinue
)

if ($buildMetaFiles.Count -eq 0) {
    $primaryReport = Join-Path -Path $ValidationReportDir -ChildPath "validation_report.json"
    if (Test-Path -LiteralPath $primaryReport) {
        $reportFiles += $primaryReport
    }

    $historyFiles = Get-ChildItem -LiteralPath $ValidationReportDir -Filter "validation_report_*.json" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 10

    foreach ($f in $historyFiles) {
        $reportFiles += $f.FullName
    }
}

$allBlockerSets = @()
foreach ($metaFile in $buildMetaFiles) {
    try {
        $data = Get-Content -LiteralPath $metaFile.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        $blockers = @()
        if ($data.validation_summary -and $data.validation_summary.blocking_statuses) {
            $blockers = @($data.validation_summary.blocking_statuses)
        }
        $allBlockerSets += @{
            timestamp = if ($data.timestamp) { [string]$data.timestamp } else { $metaFile.LastWriteTime.ToString("o") }
            blockers = @($blockers | Sort-Object -Unique)
            rom_sha256 = if ($data.rom_sha256) { [string]$data.rom_sha256 } else { $null }
            source = $metaFile.FullName
            source_kind = "build_meta"
        }
    }
    catch {
        continue
    }
}

foreach ($rf in $reportFiles) {
    try {
        $content = Get-Content -LiteralPath $rf -Raw -Encoding UTF8
        $data = $content | ConvertFrom-Json
        $blockers = @()
        if ($data.blocking_statuses) {
            $blockers = @($data.blocking_statuses)
        }
        if ($data.summary -and $data.summary.errors -gt 0) {
            if ($data.errors) {
                foreach ($err in $data.errors) {
                    if ($err.code) { $blockers += $err.code }
                }
            }
        }
        $ts = ""
        if ($data.generated_at) { $ts = $data.generated_at }
        elseif ($data.timestamp) { $ts = $data.timestamp }
        else {
            $fi = Get-Item -LiteralPath $rf
            $ts = $fi.LastWriteTime.ToString("o")
        }
        $romHash = $null
        if ($data.rom_sha256) { $romHash = $data.rom_sha256 }
        elseif ($data.rom -and $data.rom.sha256) { $romHash = $data.rom.sha256 }

        $allBlockerSets += @{
            timestamp  = $ts
            blockers   = ($blockers | Sort-Object -Unique)
            rom_sha256 = $romHash
            source     = $rf
            source_kind = "validation_report"
        }
    }
    catch {
        continue
    }
}

$allBlockerSets = @($allBlockerSets | Sort-Object { $_.timestamp })

$buildsAnalyzed = @()
$idx = 1
foreach ($bs in $allBlockerSets) {
    $buildsAnalyzed += @{
        build_index = $idx
        timestamp   = $bs.timestamp
        rom_sha256  = $bs.rom_sha256
        blockers    = $bs.blockers
        report_source = $bs.source
        source_kind = $bs.source_kind
    }
    $idx++
}

$recurringBlockers = @()
$loopDetected = $false
$commonBlockers = @()
$warningCommonBlockers = @()
$progressWarning = $false
$blockersRemoved = 0

function Get-CommonBlockers {
    param([Parameter(Mandatory = $true)][object[]]$Sets)

    if ($Sets.Count -eq 0) { return @() }
    $common = @($Sets[0].blockers)
    if ($Sets.Count -gt 1) {
        foreach ($set in $Sets[1..($Sets.Count - 1)]) {
            $common = @($common | Where-Object { $_ -in $set.blockers })
        }
    }
    return @($common | Sort-Object -Unique)
}

if ($allBlockerSets.Count -ge $Threshold) {
    $recentSets = $allBlockerSets[-$Threshold..-1]
    $commonBlockers = @(Get-CommonBlockers -Sets $recentSets)

    if ($commonBlockers -and $commonBlockers.Count -gt 0) {
        $uniqueBuildSignals = @($recentSets | ForEach-Object { $_.source }) | Sort-Object -Unique
        if ($uniqueBuildSignals.Count -ge $Threshold) {
            $loopDetected = $true
        }
    }
}

if ($allBlockerSets.Count -ge 2) {
    $previous = @($allBlockerSets[-2].blockers)
    $current = @($allBlockerSets[-1].blockers)
    $blockersRemoved = @($previous | Where-Object { $_ -notin $current }).Count
}

if ($WarningThreshold -gt 0 -and $allBlockerSets.Count -ge $WarningThreshold) {
    $warningSets = $allBlockerSets[-$WarningThreshold..-1]
    $warningCommonBlockers = @(Get-CommonBlockers -Sets $warningSets)
    $progressWarning = ($warningCommonBlockers.Count -gt 0 -and $blockersRemoved -eq 0)
}

$recurringSource = if ($commonBlockers.Count -gt 0) { $commonBlockers } else { $warningCommonBlockers }
if ($recurringSource.Count -gt 0) {
        foreach ($cb in $recurringSource) {
            $category = "other"
            if ($cb -match "visual|artistic|placeholder|art_") { $category = "visual" }
            elseif ($cb -match "perceptual|motion|animation") { $category = "perceptual_motion" }
            elseif ($cb -match "runtime|boot|scene") { $category = "runtime" }
            elseif ($cb -match "budget|vram|dma") { $category = "budget" }
            elseif ($cb -match "evidence|emulator|blastem|sram") { $category = "evidence" }
            elseif ($cb -match "doc|changelog|memory|manifest") { $category = "documentation" }
            elseif ($cb -match "infra|build|wrapper|pipeline") { $category = "infra" }

            $occurrenceCount = 0
            foreach ($bs in $allBlockerSets) {
                if ($cb -in $bs.blockers) { $occurrenceCount++ }
            }

            $recurringBlockers += @{
                blocker_code       = $cb
                occurrence_count   = $occurrenceCount
                first_seen         = $null
                dominant_category  = $category
            }
        }
}

$decisionPath = Join-Path -Path $ProjectRoot -ChildPath "doc\operational_loop_decision.json"
$decisionValid = $false
$decisionErrors = @()
$decisionSummary = $null

if ($loopDetected -and (Test-Path -LiteralPath $decisionPath)) {
    try {
        $decision = Get-Content -LiteralPath $decisionPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $requiredFields = @("schema_version", "generated_at", "project_root", "owner", "decision_date", "dominant_blockers", "strategy", "why_now_different", "progress_justification")
        foreach ($rf in $requiredFields) {
            if (-not ($decision.PSObject.Properties.Name -contains $rf)) { $decisionErrors += "missing_field:$rf" }
        }

        if ($decision.schema_version -ne "1.0.0") { $decisionErrors += "schema_version_invalid" }
        if ([string]::IsNullOrWhiteSpace([string]$decision.owner) -or ([string]$decision.owner).Length -lt 3) { $decisionErrors += "owner_invalid" }
        if ([string]::IsNullOrWhiteSpace([string]$decision.strategy) -or ([string]$decision.strategy).Length -lt 16) { $decisionErrors += "strategy_too_short" }
        if ([string]::IsNullOrWhiteSpace([string]$decision.why_now_different) -or ([string]$decision.why_now_different).Length -lt 16) { $decisionErrors += "why_now_different_too_short" }

        try { [DateTime]::Parse([string]$decision.decision_date) | Out-Null } catch { $decisionErrors += "decision_date_invalid" }

        $dominantBlockers = @()
        if ($decision.dominant_blockers) { $dominantBlockers = @($decision.dominant_blockers) }
        if ($dominantBlockers.Count -eq 0) { $decisionErrors += "dominant_blockers_missing" }
        $matchesDominant = $false
        foreach ($db in $dominantBlockers) {
            if ($db -in $commonBlockers) { $matchesDominant = $true; break }
        }
        if (-not $matchesDominant) { $decisionErrors += "dominant_blockers_do_not_match_loop" }

        $pj = $decision.progress_justification
        $hasNewEvidence = $false
        $hasMeaningfulChange = $false
        $hasHumanDecision = $false
        if ($pj) {
            if ($pj.new_evidence -and @($pj.new_evidence).Count -gt 0) { $hasNewEvidence = $true }
            if ($pj.meaningful_change_summary -and ([string]$pj.meaningful_change_summary).Length -ge 16) { $hasMeaningfulChange = $true }
            if ($pj.human_decision_record -and $pj.human_decision_record.record_path -and $pj.human_decision_record.approved_by) { $hasHumanDecision = $true }
        }
        if (-not ($hasNewEvidence -or $hasMeaningfulChange -or $hasHumanDecision)) { $decisionErrors += "progress_justification_insufficient" }

        if ($decisionErrors.Count -eq 0) {
            $decisionValid = $true
            $decisionSummary = "owner=$($decision.owner); date=$($decision.decision_date); dominant_blockers=$($dominantBlockers -join ',')"
        }
    }
    catch {
        $decisionErrors += "decision_unreadable"
    }
}

$blocking = $loopDetected -and (-not $decisionValid)
$blockerCode = if ($blocking) { "operational_loop_detected" } else { $null }

$report = [ordered]@{
    schema_version            = "1.0.0"
    generated_at              = (Get-Date -Format "o")
    project_root              = $ProjectRoot
    builds_analyzed           = $buildsAnalyzed
    recurring_blockers        = $recurringBlockers
    history_source            = if ($buildMetaFiles.Count -gt 0) { "canonical_build_meta" } else { "validation_report_history" }
    progress_warning          = $progressWarning
    warning_threshold         = $WarningThreshold
    warning_blockers          = $warningCommonBlockers
    loop_detected             = $loopDetected
    loop_threshold            = $Threshold
    strategic_decision_required = ($loopDetected -and (-not $decisionValid))
    strategic_decision        = $decisionSummary
    decision_path             = if ($loopDetected) { $decisionPath } else { $null }
    decision_valid            = if ($loopDetected) { $decisionValid } else { $null }
    decision_errors           = if ($loopDetected -and (-not $decisionValid)) { $decisionErrors } else { @() }
    progress_metrics          = [ordered]@{
        blockers_removed         = $blockersRemoved
        delivery_status_elevated = $false
        fresh_evidence_compatible = $false
        visual_art_approved      = $null
        rom_build_count_is_not_progress = $true
    }
    blocking                  = $blocking
    blocker_code              = $blockerCode
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
    $msg = "[LOOP-DETECTOR] BLOCKED: operational_loop_detected - recurring blockers in $Threshold consecutive builds."
    if ($decisionErrors.Count -gt 0) {
        $msg = "$msg decision_errors=$($decisionErrors -join ',')"
    } else {
        $msg = "$msg decision_missing=true"
    }
    Write-Warning $msg
    exit 1
}

if ($progressWarning -and -not $loopDetected) {
    Write-Warning "[LOOP-DETECTOR] WARNING: repeated blockers in $WarningThreshold consecutive builds. A specific blocker-removal intent is required before another build."
}

exit 0
