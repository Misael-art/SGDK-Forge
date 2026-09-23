$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "test_genre_no_auto_promotion.ps1") `
    -ExpectedId "platformer_precision_2d" `
    -ValidatorFile "validate_platformer_precision_2d_specialization.ps1" `
    -ReportFile "platformer_specialization_report.json"
exit $LASTEXITCODE
