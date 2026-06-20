param(
    [Parameter(Mandatory = $true)]
    [string]$ExpectedId,
    [Parameter(Mandatory = $true)]
    [string]$ValidatorFile,
    [Parameter(Mandatory = $true)]
    [string]$ReportFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$registryPath = Join-Path $workspaceRoot "doc\07_game_design\genre_specialization_registry.json"
$validatorPath = Join-Path $wrapperRoot $ValidatorFile
$fixtureRoot = Join-Path $workspaceRoot ("out\ci\no_auto_promotion_{0}" -f $ExpectedId)

if (-not (Test-Path -LiteralPath $registryPath -PathType Leaf)) {
    throw "genre_registry_missing:$registryPath"
}
if (-not (Test-Path -LiteralPath $validatorPath -PathType Leaf)) {
    throw "genre_validator_missing:$validatorPath"
}

$registryText = Get-Content -LiteralPath $registryPath -Raw -Encoding UTF8
$registry = $registryText | ConvertFrom-Json
$entry = @($registry.known_specializations | Where-Object specialization_id -eq $ExpectedId)

if ($entry.Count -ne 1) {
    throw "genre_specialization_entry_count_invalid:$($ExpectedId):$($entry.Count)"
}
if ([string]$entry[0].status -ne "active") {
    throw "genre_specialization_not_active:$ExpectedId"
}
if ([string]$registry.promotion_tier -ne "LABORATORIO") {
    throw "genre_registry_ceiling_invalid:$($registry.promotion_tier)"
}
if ($registryText -match "MESTRE_") {
    throw "genre_registry_contains_master_autopromotion"
}
foreach ($policyField in @(
    "requires_schema",
    "requires_validator",
    "requires_tests",
    "requires_explicit_opt_in"
)) {
    if (-not [bool]$registry.active_policy.$policyField) {
        throw "genre_active_policy_disabled:$policyField"
    }
}

Remove-Item -LiteralPath $fixtureRoot -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot "out\logs") | Out-Null
try {
    $global:LASTEXITCODE = 0
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $validatorPath -ProjectRoot $fixtureRoot | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "genre_validator_generalist_path_failed:$($ExpectedId):$LASTEXITCODE"
    }

    $reportPath = Join-Path $fixtureRoot ("out\logs\{0}" -f $ReportFile)
    if (-not (Test-Path -LiteralPath $reportPath -PathType Leaf)) {
        throw "genre_validator_report_missing:$reportPath"
    }
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ([string]$report.manifest_status -ne "absent" -or [string]$report.status -ne "ok") {
        throw "genre_validator_generalist_status_invalid:$ExpectedId"
    }
}
finally {
    Remove-Item -LiteralPath $fixtureRoot -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "[PASS] $ExpectedId cannot auto-promote beyond explicit active opt-in"
exit 0
