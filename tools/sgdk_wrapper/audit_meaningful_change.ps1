<#
.SYNOPSIS
    Meaningful-change gate: verifies current change attacks the dominant blocker.
.DESCRIPTION
    Reads the dominant blocker from the last validation report and checks whether
    the current change category addresses it. Wrapper/log/docs changes don't count
    when the blocker is visual/perceptual.
.PARAMETER ProjectRoot
    Root path of the SGDK project.
.PARAMETER ChangeCategory
    Category of the current change: runtime, visual, art, infra, docs, wrapper, log, schema, other.
.PARAMETER ChangeDiffSummary
    Brief description of what changed.
.PARAMETER OutputPath
    Where to write the JSON report.
.PARAMETER ValidationReportPath
    Path to the current validation_report.json (optional, auto-detected).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $false)]
    [ValidateSet("runtime", "visual", "art", "infra", "docs", "wrapper", "log", "schema", "other", "")]
    [string]$ChangeCategory = "",

    [Parameter(Mandatory = $false)]
    [string]$ChangeDiffSummary = "",

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "",

    [Parameter(Mandatory = $false)]
    [string]$ValidationReportPath = ""
)

$ErrorActionPreference = "Stop"

if ($ValidationReportPath -eq "") {
    $ValidationReportPath = Join-Path -Path $ProjectRoot -ChildPath "out\logs\validation_report.json"
}

$dominantBlocker = ""
$dominantCategory = "other"

if (Test-Path -LiteralPath $ValidationReportPath) {
    try {
        $data = Get-Content -LiteralPath $ValidationReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $blockers = @()
        if ($data.blocking_statuses) {
            $blockers = @($data.blocking_statuses)
        }
        if ($blockers.Count -gt 0) {
            $dominantBlocker = $blockers[0]

            if ($dominantBlocker -match "visual_gate|artistic|placeholder|art_|visual_direction") {
                $dominantCategory = "visual"
            }
            elseif ($dominantBlocker -match "perceptual|motion|animation") {
                $dominantCategory = "perceptual_motion"
            }
            elseif ($dominantBlocker -match "runtime|boot|scene") {
                $dominantCategory = "runtime"
            }
            elseif ($dominantBlocker -match "budget|vram|dma") {
                $dominantCategory = "budget"
            }
            elseif ($dominantBlocker -match "evidence|emulator|blastem|sram") {
                $dominantCategory = "evidence"
            }
            elseif ($dominantBlocker -match "doc|changelog|memory|manifest") {
                $dominantCategory = "documentation"
            }
        }
    }
    catch {
        # Report unreadable; skip blocker extraction
    }
}

$attacksDominant = $false
$exceptionForMeasurement = $false
$validProgress = $true

if ($dominantBlocker -ne "" -and $ChangeCategory -ne "") {
    $visualCategories = @("visual", "art")
    $runtimeCategories = @("runtime")
    $nonAttackCategories = @("docs", "wrapper", "log", "schema")

    if ($dominantCategory -eq "visual" -or $dominantCategory -eq "perceptual_motion") {
        if ($ChangeCategory -in $visualCategories) {
            $attacksDominant = $true
        }
        elseif ($ChangeCategory -in $nonAttackCategories) {
            $attacksDominant = $false
            if ($ChangeDiffSummary -match "measure|benchmark|capture|screenshot|vdp_dump|metric") {
                $exceptionForMeasurement = $true
                $attacksDominant = $true
            }
        }
        elseif ($ChangeCategory -eq "runtime") {
            $attacksDominant = $true
        }
        else {
            $attacksDominant = $false
        }
    }
    elseif ($dominantCategory -eq "runtime") {
        if ($ChangeCategory -in $runtimeCategories -or $ChangeCategory -eq "visual") {
            $attacksDominant = $true
        }
        elseif ($ChangeCategory -in $nonAttackCategories) {
            $attacksDominant = $false
        }
        else {
            $attacksDominant = $true
        }
    }
    else {
        $attacksDominant = $true
    }
}
elseif ($dominantBlocker -eq "") {
    $attacksDominant = $true
}

if (-not $attacksDominant) {
    $validProgress = $false
}

$blocking = -not $validProgress
$blockerCode = if ($blocking) { "meaningful_change_absent" } else { $null }

$report = [ordered]@{
    schema_version             = "1.0.0"
    generated_at               = (Get-Date -Format "o")
    project_root               = $ProjectRoot
    dominant_blocker           = $dominantBlocker
    dominant_category          = $dominantCategory
    change_diff_summary        = $ChangeDiffSummary
    change_category            = if ($ChangeCategory -ne "") { $ChangeCategory } else { "other" }
    attacks_dominant_blocker   = $attacksDominant
    exception_for_measurement  = $exceptionForMeasurement
    valid_progress             = $validProgress
    blocking                   = $blocking
    blocker_code               = $blockerCode
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
    Write-Warning "[MEANINGFUL-CHANGE] BLOCKED: meaningful_change_absent - Change '$ChangeCategory' does not attack dominant blocker '$dominantBlocker' ($dominantCategory)."
    exit 1
}

exit 0
