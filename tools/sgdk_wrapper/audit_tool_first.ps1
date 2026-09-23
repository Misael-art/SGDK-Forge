<#
.SYNOPSIS
    Tool-first audit: before creating new automation, evaluate existing tools and register decision.
.DESCRIPTION
    Enforces the rule that before creating new automation, the agent must:
    1. Search for existing tools in tools/
    2. Evaluate their capability
    3. Register a decision: reuse, wrap, improve, replace or reject
    4. Execute fixture or document why not
.PARAMETER ProjectRoot
    Root path of the SGDK project.
.PARAMETER AutomationDescription
    Description of the intended automation.
.PARAMETER TargetCapability
    What capability the automation should provide.
.PARAMETER Decision
    One of: reuse, wrap, improve, replace, reject.
.PARAMETER Justification
    Why this decision was made (min 8 chars).
.PARAMETER ToolPath
    Path to the existing tool being evaluated (optional).
.PARAMETER OutputPath
    Where to write the JSON report.
.PARAMETER FixtureExecuted
    Whether a fixture was executed for this tool evaluation.
.PARAMETER FixtureSkipReason
    If fixture was not executed, why (min 8 chars). Still blocks canonical use.
.PARAMETER KnownLegacyTools
    Comma-separated list of known legacy/unaudited tools.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $false)]
    [string]$AutomationDescription = "",

    [Parameter(Mandatory = $false)]
    [string]$TargetCapability = "",

    [Parameter(Mandatory = $false)]
    [ValidateSet("reuse", "wrap", "improve", "replace", "reject", "")]
    [string]$Decision = "",

    [Parameter(Mandatory = $false)]
    [string]$Justification = "",

    [Parameter(Mandatory = $false)]
    [string]$ToolPath = "",

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "",

    [Parameter(Mandatory = $false)]
    [switch]$FixtureExecuted,

    [Parameter(Mandatory = $false)]
    [string]$FixtureSkipReason = "",

    [Parameter(Mandatory = $false)]
    [string]$KnownLegacyTools = "tools/mugen2sgdk"
)

$ErrorActionPreference = "Stop"

$workspaceRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\.agent\ARCHITECTURE.md"))) {
    $workspaceRoot = Split-Path -Parent $PSScriptRoot
    while ($workspaceRoot -and -not (Test-Path -LiteralPath (Join-Path $workspaceRoot "tools\sgdk_wrapper\.agent\ARCHITECTURE.md"))) {
        $workspaceRoot = Split-Path -Parent $workspaceRoot
    }
}

$toolsRoot = Join-Path $workspaceRoot "tools"
$legacyList = $KnownLegacyTools -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }

$toolSearchResults = @()

if ($ToolPath -ne "") {
    $fullToolPath = Join-Path $workspaceRoot $ToolPath
    $toolExists = Test-Path -LiteralPath $fullToolPath
    $isLegacy = $false
    $toolStatus = "stable"

    foreach ($legacy in $legacyList) {
        $legacyFull = Join-Path $workspaceRoot $legacy
        if ($fullToolPath -like "$legacyFull*") {
            $isLegacy = $true
            $toolStatus = "legacy_unaudited"
            break
        }
    }

    $capabilityMatch = "none"
    if ($toolExists) {
        $capabilityMatch = "partial"
        if ($TargetCapability -eq "") {
            $capabilityMatch = "partial"
        }
    }

    $toolSearchResults += @{
        tool_path         = $ToolPath
        tool_name         = (Split-Path -Leaf $ToolPath)
        capability_match  = $capabilityMatch
        status            = $toolStatus
        notes             = if ($isLegacy) { "Legacy/unaudited tool. Must audit before use." } else { "" }
    }
}

$blocking = $false
$blockerCode = $null

if ($Decision -eq "" -and $AutomationDescription -ne "") {
    $blocking = $true
    $blockerCode = "tool_first_decision_absent"
}

if ($AutomationDescription -eq "" -and $Decision -eq "") {
    $blocking = $true
    $blockerCode = "tool_first_audit_missing"
}

$fixtureSkip = $FixtureSkipReason
if (-not $FixtureExecuted) {
    if ([string]::IsNullOrWhiteSpace($fixtureSkip) -or $fixtureSkip.Trim().Length -lt 8) {
        if (-not $blocking) {
            $blocking = $true
            $blockerCode = "tool_first_fixture_missing"
        }
    } else {
        if (-not $blocking) {
            $blocking = $true
            $blockerCode = "tool_first_fixture_skipped"
        }
    }
}

$report = [ordered]@{
    schema_version      = "1.0.0"
    generated_at        = (Get-Date -Format "o")
    project_root        = $ProjectRoot
    automation_intent   = [ordered]@{
        description       = $AutomationDescription
        target_capability = $TargetCapability
    }
    tool_search_results = $toolSearchResults
    fixture_executed    = [bool]$FixtureExecuted
    fixture_skip_reason = if ($FixtureExecuted) { $null } else { if ($fixtureSkip -ne "") { $fixtureSkip } else { $null } }
    fixture_result      = $null
    decision            = if ($Decision -ne "") { $Decision } else { "reject" }
    justification       = if ($Justification -ne "") { $Justification } else { "No justification provided." }
    blocking            = $blocking
    blocker_code        = $blockerCode
}

if ($OutputPath -ne "") {
    $outDir = Split-Path -Parent $OutputPath
    if ($outDir) {
        [System.IO.Directory]::CreateDirectory($outDir) | Out-Null
    }
    $report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
}

$report | ConvertTo-Json -Depth 10 -Compress | Write-Output

if ($blocking) {
    exit 1
}

exit 0
