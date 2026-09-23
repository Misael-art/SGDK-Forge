$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "test_genre_specialization_entry.ps1") -ExpectedId "platformer_precision_2d"
exit $LASTEXITCODE
