$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "test_genre_specialization_entry.ps1") -ExpectedId "strategy_tower_defense"
exit $LASTEXITCODE
