<#
.SYNOPSIS
    Audits freshness drift between canonical SGDK project artifacts.
.DESCRIPTION
    Observational wrapper tool. It checks whether compiled contracts, resource
    graph, validation, runtime capture, scene regression and emulator artifacts
    are present and newer than their declared dependencies.

    The tool does not mutate project sources. It writes only
    out/logs/freshness_audit_report.json.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectRoot = "",

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "",

    [Parameter(Mandatory = $false)]
    [switch]$Strict
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = (Get-Location).Path
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)

if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) {
    throw "ProjectRoot not found: $ProjectRoot"
}

$LogDir = Join-Path $ProjectRoot "out\logs"
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $LogDir "freshness_audit_report.json"
}
if (-not (Test-Path -LiteralPath $LogDir -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
}

function Get-RelativePath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $root = [System.IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\', '/')
    $full = [System.IO.Path]::GetFullPath($Path)
    if ($full.Equals($root, [System.StringComparison]::OrdinalIgnoreCase)) {
        return "."
    }
    if ($full.StartsWith($root + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
        return ($full.Substring($root.Length + 1) -replace '\\', '/')
    }
    return ($full -replace '\\', '/')
}

function Get-JsonOrNull {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Get-ExistingFiles {
    param([string[]]$Paths = @())

    $items = New-Object System.Collections.ArrayList
    foreach ($path in @($Paths | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })) {
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            [void]$items.Add([System.IO.Path]::GetFullPath($path))
        }
    }
    return @($items | Select-Object -Unique)
}

function Get-FilesUnder {
    param(
        [Parameter(Mandatory = $true)][string]$RelativeDir,
        [string[]]$Include = @("*")
    )

    $dir = Join-Path $ProjectRoot $RelativeDir
    if (-not (Test-Path -LiteralPath $dir -PathType Container)) {
        return @()
    }

    return @(Get-ChildItem -LiteralPath $dir -Recurse -File -Include $Include -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName)
}

function Get-LatestWriteUtc {
    param([string[]]$Paths = @())

    $latest = $null
    foreach ($path in @(Get-ExistingFiles -Paths $Paths)) {
        $stamp = (Get-Item -LiteralPath $path).LastWriteTimeUtc
        if ($null -eq $latest -or $stamp -gt $latest) {
            $latest = $stamp
        }
    }
    return $latest
}

function Get-ObservedReportStatus {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$ReportPath,
        [string[]]$DependencyPaths = @(),
        [bool]$Required = $false
    )

    $result = [ordered]@{
        name = $Name
        report_path = Get-RelativePath -Path $ReportPath
        report_present = $false
        required = [bool]$Required
        stale = $false
        generated_at = $null
        report_last_write_utc = $null
        latest_dependency_utc = $null
        dependency_count = 0
        status = "missing"
    }

    $dependencies = @(Get-ExistingFiles -Paths $DependencyPaths)
    $result.dependency_count = $dependencies.Count

    if (-not (Test-Path -LiteralPath $ReportPath -PathType Leaf)) {
        if (-not $Required) {
            $result.status = "not_observed"
        }
        return $result
    }

    $result.report_present = $true
    $reportItem = Get-Item -LiteralPath $ReportPath
    $result.report_last_write_utc = $reportItem.LastWriteTimeUtc.ToString("o")

    $json = Get-JsonOrNull -Path $ReportPath
    if ($json) {
        if ($json.PSObject.Properties['generated_at']) {
            $result.generated_at = [string]$json.generated_at
        } elseif ($json.PSObject.Properties['timestamp']) {
            $result.generated_at = [string]$json.timestamp
        }
    }

    $latestDependencyUtc = Get-LatestWriteUtc -Paths $dependencies
    if ($null -ne $latestDependencyUtc) {
        $result.latest_dependency_utc = $latestDependencyUtc.ToString("o")
        if ($latestDependencyUtc -gt $reportItem.LastWriteTimeUtc) {
            $result.stale = $true
            $result.status = "stale"
            return $result
        }
    }

    $result.status = "fresh"
    return $result
}

function Add-Finding {
    param(
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][System.Collections.ArrayList]$Findings,
        [Parameter(Mandatory = $true)][string]$Severity,
        [Parameter(Mandatory = $true)][string]$Code,
        [Parameter(Mandatory = $true)][string]$Message,
        [string]$Artifact = ""
    )

    [void]$Findings.Add([ordered]@{
        severity = $Severity
        code = $Code
        message = $Message
        artifact = $Artifact
    })
}

$specPath = Join-Path $ProjectRoot "doc\13-spec-cenas.md"
$regressionManifestPath = Join-Path $ProjectRoot "doc\scene-regression.json"
$sceneContractsPath = Join-Path $ProjectRoot "doc\scene-contracts.json"
$romPath = Join-Path $ProjectRoot "out\rom.bin"
$validationReportPath = Join-Path $ProjectRoot "out\logs\validation_report.json"
$runtimeMetricsPath = Join-Path $ProjectRoot "out\logs\runtime_metrics.json"
$sceneRegressionReportPath = Join-Path $ProjectRoot "out\logs\scene_regression_report.json"
$emulatorSessionPath = Join-Path $ProjectRoot "out\logs\emulator_session.json"
$sceneContractCompileReportPath = Join-Path $ProjectRoot "out\logs\scene_contract_compile_report.json"
$resGraphReportPath = Join-Path $ProjectRoot "out\logs\res_graph_report.json"
$audioValidationReportPath = Join-Path $ProjectRoot "out\logs\audio_validation_report.json"
$memoryBankPath = Join-Path $ProjectRoot "doc\10-memory-bank.md"
$changelogPath = Join-Path $ProjectRoot "doc\changelog\changelog.md"
$architecturePath = Join-Path $ProjectRoot "doc\03-arquitetura.md"
$methodologyManifestPath = Join-Path $ProjectRoot "doc\project_methodology_manifest.json"
$techniqueManifestPath = Join-Path $ProjectRoot "doc\technique_usage_manifest.json"
$hygieneManifestPath = Join-Path $ProjectRoot "doc\project_hygiene_manifest.json"

$resFiles = @(Get-FilesUnder -RelativeDir "res" -Include @("*.res"))
$sourceFiles = @(
    (Get-FilesUnder -RelativeDir "src" -Include @("*.c", "*.s", "*.h")),
    (Get-FilesUnder -RelativeDir "inc" -Include @("*.h")),
    $resFiles
) | ForEach-Object { $_ }
$contractFiles = @(Get-FilesUnder -RelativeDir "doc\contracts" -Include @("*.json", "*.md"))
$documentationDependencies = @(
    $sourceFiles,
    $contractFiles,
    $specPath,
    $architecturePath,
    $methodologyManifestPath,
    $techniqueManifestPath,
    $hygieneManifestPath
) | ForEach-Object { $_ }

$checks = New-Object System.Collections.ArrayList

[void]$checks.Add((Get-ObservedReportStatus `
    -Name "scene_contract_compile" `
    -ReportPath $sceneContractCompileReportPath `
    -DependencyPaths @($specPath, $regressionManifestPath, $sceneContractsPath) `
    -Required $true))

[void]$checks.Add((Get-ObservedReportStatus `
    -Name "res_graph" `
    -ReportPath $resGraphReportPath `
    -DependencyPaths $resFiles `
    -Required ($resFiles.Count -gt 0)))

[void]$checks.Add((Get-ObservedReportStatus `
    -Name "validation_report" `
    -ReportPath $validationReportPath `
    -DependencyPaths @($romPath, $runtimeMetricsPath, $sceneRegressionReportPath, $emulatorSessionPath, $sceneContractCompileReportPath, $resGraphReportPath, $audioValidationReportPath) `
    -Required $true))

[void]$checks.Add((Get-ObservedReportStatus `
    -Name "runtime_metrics" `
    -ReportPath $runtimeMetricsPath `
    -DependencyPaths @($romPath) `
    -Required $false))

[void]$checks.Add((Get-ObservedReportStatus `
    -Name "scene_regression" `
    -ReportPath $sceneRegressionReportPath `
    -DependencyPaths @($romPath, $regressionManifestPath, $sceneContractsPath) `
    -Required $false))

[void]$checks.Add((Get-ObservedReportStatus `
    -Name "emulator_session" `
    -ReportPath $emulatorSessionPath `
    -DependencyPaths @($romPath) `
    -Required $false))

[void]$checks.Add((Get-ObservedReportStatus `
    -Name "audio_validation" `
    -ReportPath $audioValidationReportPath `
    -DependencyPaths $resFiles `
    -Required $false))

$buildCheck = Get-ObservedReportStatus `
    -Name "build_output" `
    -ReportPath (Join-Path $ProjectRoot "out\logs\build_output.log") `
    -DependencyPaths $sourceFiles `
    -Required $true
[void]$checks.Add($buildCheck)

[void]$checks.Add((Get-ObservedReportStatus `
    -Name "memory_bank_sync" `
    -ReportPath $memoryBankPath `
    -DependencyPaths $documentationDependencies `
    -Required $true))

[void]$checks.Add((Get-ObservedReportStatus `
    -Name "changelog_sync" `
    -ReportPath $changelogPath `
    -DependencyPaths $documentationDependencies `
    -Required $true))

$findings = New-Object System.Collections.ArrayList
foreach ($check in $checks) {
    if ($check.required -and -not $check.report_present) {
        Add-Finding -Findings $findings -Severity "warning" -Code "FRESH_MISSING_REQUIRED" -Message ("Required freshness artifact is missing: {0}" -f $check.name) -Artifact $check.report_path
    } elseif ($check.stale) {
        Add-Finding -Findings $findings -Severity "warning" -Code "FRESH_STALE" -Message ("Artifact is stale relative to dependencies: {0}" -f $check.name) -Artifact $check.report_path
    }
    if ($check.name -eq "memory_bank_sync" -and ($check.stale -or -not $check.report_present)) {
        Add-Finding -Findings $findings -Severity "warning" -Code "FRESH_MEMORY_BANK_STALE" -Message "doc/10-memory-bank.md precisa refletir a implementacao e arquitetura vigentes." -Artifact $check.report_path
    }
    if ($check.name -eq "changelog_sync" -and ($check.stale -or -not $check.report_present)) {
        Add-Finding -Findings $findings -Severity "warning" -Code "FRESH_CHANGELOG_STALE" -Message "doc/changelog/changelog.md precisa refletir a implementacao e arquitetura vigentes." -Artifact $check.report_path
    }
}

$docs = @(
    $memoryBankPath,
    $changelogPath,
    (Join-Path $ProjectRoot "doc\13-spec-cenas.md")
)
$latestEvidenceUtc = Get-LatestWriteUtc -Paths @($validationReportPath, $runtimeMetricsPath, $sceneRegressionReportPath, $emulatorSessionPath)
foreach ($doc in @(Get-ExistingFiles -Paths $docs)) {
    if ($null -ne $latestEvidenceUtc -and (Get-Item -LiteralPath $doc).LastWriteTimeUtc -lt $latestEvidenceUtc) {
        Add-Finding -Findings $findings -Severity "info" -Code "FRESH_DOC_OLDER_THAN_EVIDENCE" -Message ("Documentation is older than latest evidence: {0}" -f (Get-RelativePath -Path $doc)) -Artifact (Get-RelativePath -Path $doc)
    }
}

$warningCount = @($findings | Where-Object { $_.severity -eq "warning" }).Count
$errorCount = @($findings | Where-Object { $_.severity -eq "error" }).Count
$status = "ok"
if ($errorCount -gt 0) {
    $status = "failed"
} elseif ($warningCount -gt 0) {
    $status = "warning"
}

$report = [ordered]@{
    schema_version = "1.0.0"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    tool_name = "freshness_audit"
    tool_version = "0.1.0"
    project_root = $ProjectRoot
    status = $status
    strict = [bool]$Strict
    summary = [ordered]@{
        checks_total = $checks.Count
        stale_count = @($checks | Where-Object { $_.stale }).Count
        missing_required_count = @($checks | Where-Object { $_.required -and -not $_.report_present }).Count
        warnings = $warningCount
        errors = $errorCount
    }
    checks = @($checks)
    findings = @($findings)
}

$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
Write-Host ("[FRESHNESS] status={0} stale={1} missing_required={2} report={3}" -f $report.status, $report.summary.stale_count, $report.summary.missing_required_count, $OutputPath)

if ($Strict -and $status -ne "ok") {
    exit 1
}
exit 0
