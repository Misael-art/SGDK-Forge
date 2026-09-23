<# 
.SYNOPSIS
    Regression test for audit_evidence_root.ps1 external path blocking with hygiene exceptions.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WrapperRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$ScriptUnderTest = Join-Path $WrapperRoot "audit_evidence_root.ps1"
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

$ProjectRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("SGDK_EVIDENCE_ROOT_TEST_[{0}]" -f ([guid]::NewGuid().ToString("N")))
$DocDir = Join-Path $ProjectRoot "doc"
$LogDir = Join-Path $ProjectRoot "out\logs"
$RascunhoDir = Join-Path $ProjectRoot "rascunho\external_input_1"
foreach ($p in @($DocDir, $LogDir, $RascunhoDir)) { [System.IO.Directory]::CreateDirectory($p) | Out-Null }

$externalSource = "C:\outside_workspace\input.png"
$hygiene = @{
    schema_version = "1.0.0"
    naming_policy = "portable_descriptive_v1"
    external_inputs = @(
        @{
            source_path = $externalSource
            copied_root = "rascunho/external_input_1"
            sha256 = "0" * 64
        }
    )
}
($hygiene | ConvertTo-Json -Depth 10) | Set-Content -LiteralPath (Join-Path $DocDir "project_hygiene_manifest.json") -Encoding UTF8

$badReport = @{
    schema_version = "1.0.0"
    generated_at = "2026-06-06T00:00:00Z"
    project_root = $ProjectRoot
    rom_path = "C:\unregistered\rom.bin"
    rom_sha256 = "1" * 64
    blocking_statuses = @()
}
($badReport | ConvertTo-Json -Depth 10) | Set-Content -LiteralPath (Join-Path $LogDir "validation_report.json") -Encoding UTF8

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest -ProjectRoot $ProjectRoot | Out-Null
Assert-True ($LASTEXITCODE -ne 0) "Expected evidence root audit to block on unregistered external path in reports"

$okReport = $badReport.Clone()
$okReport.rom_path = $externalSource
($okReport | ConvertTo-Json -Depth 10) | Set-Content -LiteralPath (Join-Path $LogDir "validation_report.json") -Encoding UTF8

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptUnderTest -ProjectRoot $ProjectRoot | Out-Null
Assert-True ($LASTEXITCODE -eq 0) "Expected evidence root audit to allow external path when registered and hashed in hygiene manifest"

Write-Host "[PASS] evidence root audit blocks external paths unless registered + hashed in hygiene manifest"

$TempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd('\', '/')
$ResolvedFixture = [System.IO.Path]::GetFullPath($ProjectRoot)
if ($ResolvedFixture.StartsWith($TempRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    Remove-Item -LiteralPath $ResolvedFixture -Recurse -Force
}
