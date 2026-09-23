<#
.SYNOPSIS
    Runs validate_resources.ps1 across all 17 AAA EFFECT LAB projects and
    writes a central readiness matrix.

.DESCRIPTION
    This is an audit/orchestration helper, not a delivery shortcut. It keeps
    each axis isolated, records the exact validator exit code, and summarizes
    blockers without promoting any project to AAA.
#>

[CmdletBinding()]
param(
    [string]$WorkspaceRoot = "",
    [string]$OutputRoot = "",
    [switch]$WarnOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
    $WorkspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
} else {
    $WorkspaceRoot = [System.IO.Path]::GetFullPath($WorkspaceRoot)
}

if (-not (Test-Path -LiteralPath $WorkspaceRoot -PathType Container)) {
    throw "WorkspaceRoot not found: $WorkspaceRoot"
}

$projectsRoot = Join-Path $WorkspaceRoot "SGDK_projects"
if (-not (Test-Path -LiteralPath $projectsRoot -PathType Container)) {
    throw "SGDK_projects not found: $projectsRoot"
}

$campaignRoot = Join-Path $projectsRoot "ProjectLab_effect_campaign [VER.001] [SGDK 211] [GEN] [HOMEBREW] [DEMO]"
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path $campaignRoot "out\logs"
}
New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

$validateScript = Join-Path $PSScriptRoot "validate_resources.ps1"
if (-not (Test-Path -LiteralPath $validateScript -PathType Leaf)) {
    throw "validate_resources.ps1 not found: $validateScript"
}

function Read-JsonOrNull {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    try {
        return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Get-Prop {
    param(
        [object]$Object,
        [string]$Name,
        [object]$Default = $null
    )
    if ($null -eq $Object) { return $Default }
    $prop = $Object.PSObject.Properties[$Name]
    if ($null -eq $prop) { return $Default }
    return $prop.Value
}

$projects = @(Get-ChildItem -LiteralPath $projectsRoot -Directory -Filter "AAA EFFECT LAB - *" | Sort-Object Name)
$rows = New-Object System.Collections.Generic.List[object]

foreach ($project in $projects) {
    $projectRoot = $project.FullName
    Write-Host ("[matrix] validate {0}" -f $project.Name)

    $validatorOutput = & powershell -NoProfile -ExecutionPolicy Bypass -File $validateScript -WorkDir $projectRoot -CloseoutGate 2>&1
    $exitCode = $LASTEXITCODE
    $validationPath = Join-Path $projectRoot "out\logs\validation_report.json"
    $validation = Read-JsonOrNull -Path $validationPath

    $statusPanel = Get-Prop $validation "status_panel" $null
    $productTaxonomy = Get-Prop $validation "product_taxonomy" $null
    $qaAxes = Get-Prop $validation "qa_axes" $null
    $blockingStatuses = @(Get-Prop $validation "blocking_statuses" @())

    $rows.Add([pscustomobject][ordered]@{
        project = $project.Name
        project_root = $projectRoot
        validator_exit_code = $exitCode
        validation_report = $validationPath
        ready_for_aaa = [bool](Get-Prop $statusPanel "ready_for_aaa" $false)
        technical_ready = [bool](Get-Prop $statusPanel "technical_ready" $false)
        creative_ready = [bool](Get-Prop $statusPanel "creative_ready" $false)
        product_status = [string](Get-Prop $productTaxonomy "product_status" "")
        claim_ceiling = [string](Get-Prop $productTaxonomy "claim_ceiling" "")
        max_delivery_status = [string](Get-Prop $statusPanel "max_delivery_status" "")
        build = [string](Get-Prop $qaAxes "build" "")
        gameplay = [string](Get-Prop $qaAxes "gameplay_basico" "")
        performance = [string](Get-Prop $qaAxes "performance" "")
        audio = [string](Get-Prop $qaAxes "audio" "")
        blockers = @($blockingStatuses)
        output_tail = @($validatorOutput | Select-Object -Last 12)
    }) | Out-Null
}

$readyCount = @($rows | Where-Object { $_.ready_for_aaa }).Count
$blockedCount = @($rows | Where-Object { -not $_.ready_for_aaa }).Count
$badLabCeilingCount = @($rows | Where-Object {
    $_.product_status -ne "technical_lab_validated" -or $_.claim_ceiling -eq "ready_for_aaa"
}).Count

$report = [ordered]@{
    schema_version = "1.0.0"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    tool_name = "run_effect_lab_validation_matrix"
    workspace_root = $WorkspaceRoot
    expected_project_count = 17
    project_count = $projects.Count
    ready_for_aaa_count = $readyCount
    blocked_count = $blockedCount
    bad_lab_ceiling_count = $badLabCeilingCount
    status = if ($projects.Count -eq 17 -and $readyCount -eq 0 -and $badLabCeilingCount -eq 0) { "prototype_debug_lab_reclassified" } else { "needs_attention" }
    rows = @($rows.ToArray())
}

$jsonPath = Join-Path $OutputRoot "aaa_effect_lab_validation_matrix.json"
$mdPath = Join-Path $OutputRoot "aaa_effect_lab_validation_matrix.md"
$report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# AAA Effect Lab Validation Matrix") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("- status: $($report.status)") | Out-Null
$lines.Add("- project_count: $($report.project_count)") | Out-Null
$lines.Add("- ready_for_aaa_count: $($report.ready_for_aaa_count)") | Out-Null
$lines.Add("- blocked_count: $($report.blocked_count)") | Out-Null
$lines.Add("- bad_lab_ceiling_count: $($report.bad_lab_ceiling_count)") | Out-Null
$lines.Add("") | Out-Null
foreach ($row in $rows) {
    $lines.Add("- $($row.project): ready_for_aaa=$($row.ready_for_aaa), product_status=$($row.product_status), claim_ceiling=$($row.claim_ceiling)") | Out-Null
    foreach ($blocker in @($row.blockers | Select-Object -First 10)) {
        $lines.Add("  - blocker: $blocker") | Out-Null
    }
}
$lines | Set-Content -LiteralPath $mdPath -Encoding UTF8

Write-Host ("[matrix] status={0} report={1}" -f $report.status, $jsonPath)

if ($report.status -ne "prototype_debug_lab_reclassified" -and -not $WarnOnly) {
    exit 1
}
exit 0

