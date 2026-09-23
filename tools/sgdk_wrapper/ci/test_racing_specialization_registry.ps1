$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "test_genre_specialization_entry.ps1") -ExpectedId "racing_arcade"
exit $LASTEXITCODE
