$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "test_genre_no_auto_promotion.ps1") `
    -ExpectedId "racing_arcade" `
    -ValidatorFile "validate_racing_arcade_specialization.ps1" `
    -ReportFile "racing_specialization_report.json"
exit $LASTEXITCODE
