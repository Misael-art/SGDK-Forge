<# 
.SYNOPSIS
    Regression test for audit_orphan_subproject.ps1 root aggregation rules.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$ScriptUnderTest = Join-Path $WrapperRoot "audit_orphan_subproject.ps1"
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

$ProjectRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("SGDK_ORPHAN_TEST_[{0}]" -f ([guid]::NewGuid().ToString("N")))
$MddevDir = Join-Path $ProjectRoot ".mddev"
$DocDir = Join-Path $ProjectRoot "doc"
$LogDir = Join-Path $ProjectRoot "out\logs"
foreach ($p in @($MddevDir, $DocDir, (Join-Path $DocDir "changelog"), $LogDir)) { [System.IO.Directory]::CreateDirectory($p) | Out-Null }

$nestedRel = "viewer_sub\viewer"
$projectJson = @{
    name = "orphan_test"
    display_name = "orphan_test"
    nested_viewers = @($nestedRel)
}
($projectJson | ConvertTo-Json -Depth 10) | Set-Content -LiteralPath (Join-Path $MddevDir "project.json") -Encoding UTF8

Set-Content -LiteralPath (Join-Path $DocDir "10-memory-bank.md") -Value ("viewer: {0}`n" -f $nestedRel) -Encoding UTF8
Set-Content -LiteralPath (Join-Path $DocDir "changelog\changelog.md") -Value "objective_closed: true`ncloseout: ok`n" -Encoding UTF8
Set-Content -LiteralPath (Join-Path $LogDir "validation_report.json") -Value "{`"generated_at`":`"2026-06-06T00:00:00Z`"}" -Encoding UTF8

$viewerDir = Join-Path $ProjectRoot $nestedRel
foreach ($p in @($viewerDir, (Join-Path $viewerDir "src"), (Join-Path $viewerDir "res"))) { [System.IO.Directory]::CreateDirectory($p) | Out-Null }
Set-Content -LiteralPath (Join-Path $viewerDir "Makefile") -Value "all:`n`t@echo ok`n" -Encoding UTF8

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest -ProjectRoot $ProjectRoot | Out-Null
Assert-True ($LASTEXITCODE -eq 0) "Expected orphan subproject audit to pass when root aggregates nested viewer"

$projectJson2 = @{
    name = "orphan_test"
    display_name = "orphan_test"
}
($projectJson2 | ConvertTo-Json -Depth 10) | Set-Content -LiteralPath (Join-Path $MddevDir "project.json") -Encoding UTF8

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest -ProjectRoot $ProjectRoot | Out-Null
Assert-True ($LASTEXITCODE -ne 0) "Expected orphan subproject audit to block when nested_viewers is missing in root project.json"

Write-Host "[PASS] orphan subproject audit validates root aggregation via .mddev/project.json nested_viewers"

$TempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd('\', '/')
$ResolvedFixture = [System.IO.Path]::GetFullPath($ProjectRoot)
if ($ResolvedFixture.StartsWith($TempRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    Remove-Item -LiteralPath $ResolvedFixture -Recurse -Force
}
