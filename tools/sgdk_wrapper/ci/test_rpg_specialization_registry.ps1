$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "test_genre_specialization_entry.ps1") -ExpectedId "rpg_turn_based_jrpg"
exit $LASTEXITCODE
