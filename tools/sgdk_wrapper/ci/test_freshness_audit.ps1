<# 
.SYNOPSIS
    Smoke test for tools/sgdk_wrapper/freshness_audit.ps1.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$ScriptUnderTest = Join-Path $WrapperRoot "freshness_audit.ps1"
$ValidateResourcesScript = Join-Path $WrapperRoot "validate_resources.ps1"
if (-not (Test-Path -LiteralPath $ScriptUnderTest -PathType Leaf)) {
    throw "Script under test not found: $ScriptUnderTest"
}

function Assert-True {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )

    if (-not $Condition) {
        throw $Message
    }
}

$ProjectRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("sgdk_freshness_audit_test_{0}" -f ([guid]::NewGuid().ToString("N")))
$DocDir = Join-Path $ProjectRoot "doc"
$LogDir = Join-Path $ProjectRoot "out\logs"
$ResDir = Join-Path $ProjectRoot "res"
$SrcDir = Join-Path $ProjectRoot "src"
New-Item -ItemType Directory -Force -Path $DocDir, $LogDir, $ResDir, $SrcDir | Out-Null

$SpecPath = Join-Path $DocDir "13-spec-cenas.md"
$RegressionManifestPath = Join-Path $DocDir "scene-regression.json"
$ContractsPath = Join-Path $DocDir "scene-contracts.json"
$MemoryPath = Join-Path $DocDir "10-memory-bank.md"
$ChangelogPath = Join-Path $DocDir "changelog\changelog.md"
$BuildLogPath = Join-Path $LogDir "build_output.log"
$CompileReportPath = Join-Path $LogDir "scene_contract_compile_report.json"
$ValidationReportPath = Join-Path $LogDir "validation_report.json"
$RomPath = Join-Path $ProjectRoot "out\rom.bin"

[System.IO.File]::WriteAllText($SpecPath, "# spec`n", [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllText($RegressionManifestPath, "{}`n", [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllText($ContractsPath, "{}`n", [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllText($MemoryPath, "# memory`n", [System.Text.Encoding]::UTF8)
[System.IO.Directory]::CreateDirectory((Split-Path $ChangelogPath -Parent)) | Out-Null
[System.IO.File]::WriteAllText($ChangelogPath, "# changelog`n", [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllText((Join-Path $SrcDir "main.c"), "int main(void){return 0;}`n", [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllText($BuildLogPath, "build ok`n", [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllText($ValidationReportPath, "{`"generated_at`":`"2026-01-01T00:00:00Z`"}`n", [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllText($CompileReportPath, "{`"generated_at`":`"2026-01-01T00:00:00Z`"}`n", [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllBytes($RomPath, [byte[]](1, 2, 3, 4))

$old = [datetime]::UtcNow.AddMinutes(-20)
$new = [datetime]::UtcNow.AddMinutes(-5)
[System.IO.File]::SetLastWriteTimeUtc($CompileReportPath, $old)
[System.IO.File]::SetLastWriteTimeUtc($SpecPath, $new)
[System.IO.File]::SetLastWriteTimeUtc($MemoryPath, $old)
[System.IO.File]::SetLastWriteTimeUtc($ChangelogPath, $old)
[System.IO.File]::SetLastWriteTimeUtc((Join-Path $SrcDir "main.c"), $new)

& $ScriptUnderTest -ProjectRoot $ProjectRoot
if ($LASTEXITCODE -ne 0) {
    throw "freshness_audit.ps1 exited with code $LASTEXITCODE"
}

$ReportPath = Join-Path $LogDir "freshness_audit_report.json"
Assert-True (Test-Path -LiteralPath $ReportPath -PathType Leaf) "freshness_audit_report.json was not written"
$report = Get-Content -LiteralPath $ReportPath -Raw | ConvertFrom-Json

Assert-True ($report.status -eq "warning") "Expected warning status, got '$($report.status)'"
Assert-True ([int]$report.summary.stale_count -ge 1) "Expected at least one stale artifact"

$sceneContractCheck = @($report.checks | Where-Object { $_.name -eq "scene_contract_compile" })[0]
Assert-True ([bool]$sceneContractCheck.stale) "Expected scene_contract_compile to be stale"
Assert-True (@($report.findings | Where-Object { $_.code -eq "FRESH_MEMORY_BANK_STALE" }).Count -ge 1) "Expected stale memory bank finding"
Assert-True (@($report.findings | Where-Object { $_.code -eq "FRESH_CHANGELOG_STALE" }).Count -ge 1) "Expected stale changelog finding"

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ValidateResourcesScript -WorkDir $ProjectRoot -CloseoutGate | Out-Null
$ValidationReport = Get-Content -LiteralPath $ValidationReportPath -Raw | ConvertFrom-Json
Assert-True (@($ValidationReport.blocking_statuses) -contains "freshness_audit_stale") "Expected validate_resources closeout to propagate stale findings from freshness_audit_report.json"
Assert-True (@($ValidationReport.blocking_statuses) -contains "project_documentation_sync_stale") "Expected validate_resources closeout to expose documentation sync drift"

Write-Host "[PASS] freshness_audit smoke detected stale canonical artifact"
Write-Host "[PASS] validate_resources propagated freshness_audit_stale"
Write-Host "[PASS] memory bank and changelog drift block project closeout"
$TempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd('\', '/')
$ResolvedFixture = [System.IO.Path]::GetFullPath($ProjectRoot)
if ($ResolvedFixture.StartsWith($TempRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    Remove-Item -LiteralPath $ResolvedFixture -Recurse -Force
    Write-Host "[INFO] Temp project removed: $ResolvedFixture"
}
