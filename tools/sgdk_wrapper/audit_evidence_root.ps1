<#
.SYNOPSIS
    Evidence root isolation: blocks when reports point to another workspace/project.
.DESCRIPTION
    Scans validation_report.json, scene_regression_report.json, emulator_session.json
    and closeout manifests. Blocks if project_root points outside active project or
    ROM hash differs across artifacts.
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

$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot -ErrorAction SilentlyContinue).Path
if (-not $ProjectRoot) {
    Write-Error "ProjectRoot not found."
    exit 1
}

$logDir = Join-Path -Path $ProjectRoot -ChildPath "out\logs"

$reportedRoots = @()
$romHashes = @()
$rootMismatch = $false
$hashDivergent = $false
$externalPathsAccepted = @()
$externalPathViolations = @()

$reportFiles = @(
    "validation_report.json",
    "scene_regression_report.json",
    "emulator_session.json",
    "visual_delivery_gate_report.json",
    "scene_closeout_gate_report.json",
    "runtime_metrics.json",
    "freshness_audit_report.json",
    "res_graph_report.json"
)

foreach ($rf in $reportFiles) {
    $fullPath = Join-Path -Path $logDir -ChildPath $rf
    if (-not (Test-Path -LiteralPath $fullPath)) { continue }

    try {
        $data = Get-Content -LiteralPath $fullPath -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    catch { continue }

    $rootFields = @("project_root", "ProjectRoot", "project_path")
    foreach ($field in $rootFields) {
        $val = $data.$field
        if ($val -and $val -is [string] -and $val.Length -gt 0) {
            $normalizedVal = $val.TrimEnd("\", "/")
            $normalizedProject = $ProjectRoot.TrimEnd("\", "/")
            $inside = ($normalizedVal -eq $normalizedProject) -or ($normalizedVal -like "$normalizedProject\*") -or ($normalizedVal -like "$normalizedProject/*")

            $reportedRoots += @{
                source_file    = $rf
                reported_root  = $val
                inside_project = $inside
                field_name     = $field
            }

            if (-not $inside) { $rootMismatch = $true }
        }
    }

    $hashFields = @("rom_sha256", "rom_hash", "baseline_rom_sha256", "current_rom_sha256")
    foreach ($hf in $hashFields) {
        $val = $data.$hf
        if ($val -and $val -is [string] -and $val -match "^[a-f0-9]{64}$") {
            $romHashes += @{
                source_file = $rf
                rom_sha256  = $val
                context     = $hf
            }
        }
    }

    if ($data.rom -and $data.rom.sha256) {
        $romHashes += @{
            source_file = $rf
            rom_sha256  = $data.rom.sha256
            context     = "rom.sha256"
        }
    }

    if ($data.runtime_metrics -and $data.runtime_metrics.rom_sha256) {
        $romHashes += @{
            source_file = $rf
            rom_sha256  = $data.runtime_metrics.rom_sha256
            context     = "runtime_metrics.rom_sha256"
        }
    }
}

$uniqueHashes = $romHashes | ForEach-Object { $_.rom_sha256 } | Sort-Object -Unique
if ($uniqueHashes.Count -gt 1) {
    $hashDivergent = $true
}

$rascunhoDir = Join-Path -Path $ProjectRoot -ChildPath "rascunho"
$hygienePath = Join-Path -Path $ProjectRoot -ChildPath "doc\project_hygiene_manifest.json"
$acceptedExternalSourcePaths = @()
if (Test-Path -LiteralPath $hygienePath) {
    try {
        $hygiene = Get-Content -LiteralPath $hygienePath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($hygiene.external_inputs) {
            foreach ($ei in $hygiene.external_inputs) {
                $copied = $false
                $hashOk = $false
                if ($ei.copied_root -and (Test-Path -LiteralPath (Join-Path -Path $ProjectRoot -ChildPath $ei.copied_root))) {
                    $copied = $true
                }
                if ($ei.sha256) { $hashOk = $true }
                $externalPathsAccepted += @{
                    path           = if ($ei.source_path) { $ei.source_path } else { "unknown" }
                    rascunho_copy  = $copied
                    hash_verified  = $hashOk
                }
                if ($copied -and $hashOk -and $ei.source_path) {
                    $acceptedExternalSourcePaths += [string]$ei.source_path
                }
            }
        }
    }
    catch {}
}

function Get-AbsolutePathsFromObject {
    param(
        [Parameter(Mandatory = $true)]$Value,
        [string]$Source = ""
    )

    $paths = New-Object System.Collections.Generic.List[object]
    if ($null -eq $Value) { return $paths }

    if ($Value -is [string]) {
        $s = [string]$Value
        if ($s -match "^(?:[A-Za-z]:[\\/]|\\\\\\\\)") {
            $paths.Add(@{ source = $Source; path = $s })
        }
        return $paths
    }

    if ($Value -is [System.Collections.IDictionary]) {
        foreach ($k in $Value.Keys) {
            $childSource = if ($Source -ne "") { "$Source.$k" } else { [string]$k }
            foreach ($p in (Get-AbsolutePathsFromObject -Value $Value[$k] -Source $childSource)) { $paths.Add($p) }
        }
        return $paths
    }

    if ($Value -is [System.Collections.IEnumerable] -and -not ($Value -is [string])) {
        $i = 0
        foreach ($item in $Value) {
            $childSource = if ($Source -ne "") { "$Source[$i]" } else { "[$i]" }
            foreach ($p in (Get-AbsolutePathsFromObject -Value $item -Source $childSource)) { $paths.Add($p) }
            $i++
        }
        return $paths
    }

    if ($Value.PSObject -and $Value.PSObject.Properties) {
        foreach ($prop in $Value.PSObject.Properties) {
            $childSource = if ($Source -ne "") { "$Source.$($prop.Name)" } else { $prop.Name }
            foreach ($p in (Get-AbsolutePathsFromObject -Value $prop.Value -Source $childSource)) { $paths.Add($p) }
        }
        return $paths
    }

    return $paths
}

foreach ($rf in $reportFiles) {
    $fullPath = Join-Path -Path $logDir -ChildPath $rf
    if (-not (Test-Path -LiteralPath $fullPath)) { continue }
    try {
        $data = Get-Content -LiteralPath $fullPath -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    catch { continue }

    $paths = Get-AbsolutePathsFromObject -Value $data -Source $rf
    foreach ($p in $paths) {
        $abs = [string]$p.path
        $isInside = $false
        try {
            $resolved = (Resolve-Path -LiteralPath $abs -ErrorAction SilentlyContinue).Path
            if ($resolved) {
                $normalizedProject = $ProjectRoot.TrimEnd("\", "/")
                $normalizedResolved = $resolved.TrimEnd("\", "/")
                $isInside = ($normalizedResolved -eq $normalizedProject) -or ($normalizedResolved -like "$normalizedProject\*") -or ($normalizedResolved -like "$normalizedProject/*")
            }
        } catch {}

        if ($isInside) { continue }
        if ($acceptedExternalSourcePaths -contains $abs) { continue }

        $externalPathViolations += @{
            source_file = $rf
            field_path  = $p.source
            external_path = $abs
            accepted_by_hygiene_manifest = $false
        }
    }
}

$blockerCodes = @()
if ($rootMismatch) { $blockerCodes += "evidence_root_mismatch" }
if ($hashDivergent) { $blockerCodes += "evidence_rom_hash_divergent" }
if ($externalPathViolations.Count -gt 0) { $blockerCodes += "evidence_external_path_detected" }

$blocking = $blockerCodes.Count -gt 0

$report = [ordered]@{
    schema_version          = "1.0.0"
    generated_at            = (Get-Date -Format "o")
    project_root            = $ProjectRoot
    expected_root           = $ProjectRoot
    reported_roots          = $reportedRoots
    rom_hashes              = $romHashes
    root_mismatch           = $rootMismatch
    hash_divergent          = $hashDivergent
    external_paths_accepted = $externalPathsAccepted
    external_path_violations = $externalPathViolations
    blocking                = $blocking
    blocker_codes           = $blockerCodes
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
    Write-Warning "[EVIDENCE-ROOT] BLOCKED: $($blockerCodes -join ', ')"
    exit 1
}

exit 0
