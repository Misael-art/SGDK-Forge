$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "test_genre_specialization_entry.ps1") -ExpectedId "fighting_2d_traditional"
exit $LASTEXITCODE
