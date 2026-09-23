<#
.SYNOPSIS
    Orphan subproject detection: finds nested SGDK viewers/studies without proper aggregation.
.DESCRIPTION
    If a project contains nested SGDK viewer or study subdirectories, verifies the root has:
    aggregator manifest, memory bank, changelog, link to viewer, evidence or lab status,
    and original objective closure.
.PARAMETER ProjectRoot
    Root path of the SGDK project.
.PARAMETER OutputPath
    Where to write the JSON report.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"

$nestedProjects = @()

$viewerIndicators = @("Makefile", "makefile.gen", "rom_head.bin", ".mddev")
$studyKeywords = @("viewer", "study", "techdemo", "lab", "experiment", "benchmark", "showdown")

$candidateDirs = Get-ChildItem -LiteralPath $ProjectRoot -Directory -Recurse -Depth 3 -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -ne $ProjectRoot -and
        $_.FullName -notlike "*\out*" -and
        $_.FullName -notlike "*\rascunho*" -and
        $_.FullName -notlike "*\.agent*" -and
        $_.FullName -notlike "*\.mddev*" -and
        $_.FullName -notlike "*\.git*" -and
        $_.FullName -notlike "*\sdk\*" -and
        $_.FullName -notlike "*\res\*" -and
        $_.FullName -notlike "*\data\*"
    }

foreach ($dir in $candidateDirs) {
    $isViewer = $false
    $kind = "study"

    foreach ($indicator in $viewerIndicators) {
        $indicatorPath = Join-Path -Path $dir.FullName -ChildPath $indicator
        if (Test-Path -LiteralPath $indicatorPath) {
            $isViewer = $true
            if ($indicator -eq "Makefile" -or $indicator -eq "makefile.gen") {
                $kind = "viewer_sgdk"
            }
            break
        }
    }

    if (-not $isViewer) {
        $dirLower = $dir.Name.ToLower()
        foreach ($kw in $studyKeywords) {
            if ($dirLower -match [regex]::Escape($kw)) {
                $isViewer = $true
                if ($dirLower -match "viewer") { $kind = "viewer_sgdk" }
                elseif ($dirLower -match "techdemo|benchmark") { $kind = "techdemo" }
                elseif ($dirLower -match "lab|experiment") { $kind = "lab_experiment" }
                break
            }
        }
    }

    if (-not $isViewer) { continue }

    $hasSrc = Test-Path -LiteralPath (Join-Path -Path $dir.FullName -ChildPath "src")
    $hasRes = Test-Path -LiteralPath (Join-Path -Path $dir.FullName -ChildPath "res")
    if (-not $hasSrc -and -not $hasRes) { continue }

    $relPath = $dir.FullName.Substring($ProjectRoot.Length + 1)

    $aggregatorManifest = $false
    $memoryBank = $false
    $changelog = $false
    $viewerLink = $false
    $evidenceOrLab = $false
    $objectiveClosed = $false
    $missingItems = @()

    $rootProjectJsonPath = Join-Path -Path $ProjectRoot -ChildPath ".mddev\project.json"
    if (Test-Path -LiteralPath $rootProjectJsonPath) {
        try {
            $rootProjectJson = Get-Content -LiteralPath $rootProjectJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($rootProjectJson.PSObject.Properties.Name -contains "nested_viewers" -and $rootProjectJson.nested_viewers) {
                $declared = @($rootProjectJson.nested_viewers | ForEach-Object { [string]$_ })
                foreach ($d in $declared) {
                    if ([string]::IsNullOrWhiteSpace($d)) { continue }
                    $norm = $d.Trim().TrimStart("\", "/").Replace("/", "\")
                    if ($norm -eq $relPath -or $norm -eq ($relPath.Replace("/", "\"))) {
                        $aggregatorManifest = $true
                        break
                    }
                }
            }
        } catch {}
    }
    if (-not $aggregatorManifest) { $missingItems += "root_project_json_nested_viewers_missing" }

    $mbPath = Join-Path -Path $ProjectRoot -ChildPath "doc\10-memory-bank.md"
    if (Test-Path -LiteralPath $mbPath) { $memoryBank = $true } else { $missingItems += "root_memory_bank_missing" }

    $clPath = Join-Path -Path $ProjectRoot -ChildPath "doc\changelog\changelog.md"
    if (Test-Path -LiteralPath $clPath) { $changelog = $true } else { $missingItems += "root_changelog_missing" }

    if ($memoryBank) {
        $rootMemContent = Get-Content -LiteralPath $mbPath -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        if ($rootMemContent -and ($rootMemContent -match [regex]::Escape($relPath) -or $rootMemContent -match [regex]::Escape($dir.Name))) {
            $viewerLink = $true
        }
    }
    if (-not $viewerLink) { $missingItems += "viewer_link_missing_in_root_memory" }

    $outDir = Join-Path -Path $ProjectRoot -ChildPath "out"
    $hasEvidence = $false
    if (Test-Path -LiteralPath $outDir) {
        $evidenceFiles = Get-ChildItem -LiteralPath $outDir -Recurse -Include "*.json", "*.png", "*.bin", "*.sram" -ErrorAction SilentlyContinue
        if ($evidenceFiles -and $evidenceFiles.Count -gt 0) { $hasEvidence = $true }
    }
    $labMarker = Join-Path -Path $ProjectRoot -ChildPath "lab_status.json"
    $labMarkerDoc = Join-Path -Path $ProjectRoot -ChildPath "doc\lab_status.json"
    if ($hasEvidence -or (Test-Path -LiteralPath $labMarker) -or (Test-Path -LiteralPath $labMarkerDoc)) {
        $evidenceOrLab = $true
    }
    else { $missingItems += "root_evidence_or_lab_status_missing" }

    if ($changelog) {
        $clContent = Get-Content -LiteralPath $clPath -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        if ($clContent -and (($clContent -match "objective_closed") -or ($clContent -match "closeout") -or ($clContent -match "encerr") -or ($clContent -match "finaliz"))) {
            $objectiveClosed = $true
        }
    }
    if (-not $objectiveClosed) { $missingItems += "objective_closure_missing_in_root_changelog" }

    $orphan = -not ($aggregatorManifest -and $memoryBank -and $changelog -and $viewerLink -and $evidenceOrLab -and $objectiveClosed)

    $nestedProjects += @{
        path                        = $relPath
        kind                        = $kind
        aggregator_manifest_present = $aggregatorManifest
        memory_bank_present         = $memoryBank
        changelog_present           = $changelog
        viewer_link_present         = $viewerLink
        evidence_or_lab_status      = $evidenceOrLab
        objective_closed            = $objectiveClosed
        missing_items               = $missingItems
    }
}

$orphanDetected = ($nestedProjects | Where-Object {
    -not ($_.aggregator_manifest_present -and $_.memory_bank_present -and $_.changelog_present -and $_.viewer_link_present -and $_.evidence_or_lab_status -and $_.objective_closed)
}).Count -gt 0

$blocking = $orphanDetected
$blockerCode = if ($orphanDetected) { "orphan_subproject_detected" } else { $null }

$report = [ordered]@{
    schema_version   = "1.0.0"
    generated_at     = (Get-Date -Format "o")
    project_root     = $ProjectRoot
    nested_projects  = $nestedProjects
    orphan_detected  = $orphanDetected
    blocking         = $blocking
    blocker_code     = $blockerCode
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
    Write-Warning "[ORPHAN-SUBPROJECT] BLOCKED: orphan_subproject_detected - $($nestedProjects.Count) nested project(s) without proper aggregation."
    exit 1
}

exit 0
