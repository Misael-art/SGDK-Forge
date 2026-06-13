<# 
.SYNOPSIS
    Regression test for audit_tool_first.ps1 fixture gating.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$ScriptUnderTest = Join-Path $WrapperRoot "audit_tool_first.ps1"
if (-not (Test-Path -LiteralPath $ScriptUnderTest -PathType Leaf)) {
    throw "Script under test not found: $ScriptUnderTest"
}

function Assert-True {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if (-not $Condition) { throw $Message }
}

$ProjectRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("SGDK_TOOL_FIRST_TEST_[{0}]" -f ([guid]::NewGuid().ToString("N")))
[System.IO.Directory]::CreateDirectory($ProjectRoot) | Out-Null

$output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest `
    -ProjectRoot $ProjectRoot `
    -AutomationDescription "new automation" `
    -TargetCapability "convert sprites" `
    -Decision "wrap" `
    -Justification "fixture not available yet" `
    -ToolPath "tools/mugen2sgdk" `
    -FixtureSkipReason "fixture_not_available_for_tool_yet" 2>$null

Assert-True ($LASTEXITCODE -ne 0) "Expected tool-first audit to block when fixture is skipped"
$jsonLine = @($output) | Where-Object { $_ -is [string] -and $_.TrimStart().StartsWith('{') } | Select-Object -Last 1
Assert-True (-not [string]::IsNullOrWhiteSpace($jsonLine)) "Expected JSON output from tool-first audit"
$report = $jsonLine | ConvertFrom-Json
Assert-True ($report.fixture_executed -eq $false) "Expected fixture_executed=false"
Assert-True ($report.fixture_skip_reason -and $report.fixture_skip_reason.Length -ge 8) "Expected fixture_skip_reason to be recorded"
Assert-True ($report.blocker_code -eq "tool_first_fixture_skipped") "Expected blocker_code=tool_first_fixture_skipped"

$output2 = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest `
    -ProjectRoot $ProjectRoot `
    -AutomationDescription "new automation" `
    -TargetCapability "convert sprites" `
    -Decision "wrap" `
    -Justification "fixture missing should block" `
    -ToolPath "tools/mugen2sgdk" `
    2>$null

Assert-True ($LASTEXITCODE -ne 0) "Expected tool-first audit to block when fixture is missing"
$jsonLine2 = @($output2) | Where-Object { $_ -is [string] -and $_.TrimStart().StartsWith('{') } | Select-Object -Last 1
Assert-True (-not [string]::IsNullOrWhiteSpace($jsonLine2)) "Expected JSON output from tool-first audit (missing fixture)"
$report2 = $jsonLine2 | ConvertFrom-Json
Assert-True ($report2.blocker_code -eq "tool_first_fixture_missing") "Expected blocker_code=tool_first_fixture_missing"

Write-Host "[PASS] tool-first audit blocks when fixture is skipped or missing (LiteralPath-safe)"

$TempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd('\', '/')
$ResolvedFixture = [System.IO.Path]::GetFullPath($ProjectRoot)
if ($ResolvedFixture.StartsWith($TempRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    Remove-Item -LiteralPath $ResolvedFixture -Recurse -Force
}
