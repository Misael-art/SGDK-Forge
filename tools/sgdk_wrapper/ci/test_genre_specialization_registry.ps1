<#
.SYNOPSIS
    Verifies that only implemented genre specializations are active.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WrapperRoot = Split-Path $PSScriptRoot -Parent
$WorkspaceRoot = Split-Path (Split-Path $WrapperRoot -Parent) -Parent
$RegistryPath = Join-Path $WorkspaceRoot "doc\07_game_design\genre_specialization_registry.json"

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

Assert-True (Test-Path -LiteralPath $RegistryPath -PathType Leaf) "genre registry missing"
$registry = Get-Content -LiteralPath $RegistryPath -Raw -Encoding UTF8 | ConvertFrom-Json
$known = @($registry.known_specializations)
$active = @($known | Where-Object { $_.status -eq "active" })
$deferred = @($known | Where-Object { $_.status -eq "deferred" })

$expectedActive = @(
    "fighting_2d_traditional",
    "brawler_belt_scroll",
    "platformer_precision_2d",
    "racing_arcade",
    "rpg_turn_based_jrpg",
    "strategy_tower_defense"
)

Assert-True ($known.Count -eq 38) "expected 38 registered specializations"
Assert-True ($active.Count -eq 6) "expected exactly six operationally active specializations"
Assert-True ($deferred.Count -eq 32) "expected 32 deferred specializations"

foreach ($id in $expectedActive) {
    $entry = $active | Where-Object { $_.specialization_id -eq $id } | Select-Object -First 1
    Assert-True ($null -ne $entry) "active specialization missing: $id"
    Assert-True (-not [string]::IsNullOrWhiteSpace([string]$entry.design_contract_schema)) "active schema missing: $id"
    Assert-True (-not [string]::IsNullOrWhiteSpace([string]$entry.validator)) "active validator missing: $id"
    Assert-True (Test-Path -LiteralPath (Join-Path $WrapperRoot "schemas\$($entry.design_contract_schema)") -PathType Leaf) "schema file missing: $id"
    Assert-True (Test-Path -LiteralPath (Join-Path $WrapperRoot $entry.validator) -PathType Leaf) "validator file missing: $id"
    Assert-True (Test-Path -LiteralPath (Join-Path $WorkspaceRoot "$($entry.owner_skill)\SKILL.md") -PathType Leaf) "owner skill missing: $id"
}

foreach ($entry in $deferred) {
    Assert-True ($null -eq $entry.design_contract_schema) "deferred specialization claims schema: $($entry.specialization_id)"
    Assert-True ($null -eq $entry.validator) "deferred specialization claims validator: $($entry.specialization_id)"
}

Write-Host "[PASS] genre registry activates only implemented specializations"
