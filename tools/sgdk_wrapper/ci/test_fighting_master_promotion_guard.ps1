$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "test_genre_no_auto_promotion.ps1") `
    -ExpectedId "fighting_2d_traditional" `
    -ValidatorFile "validate_fighting_specialization.ps1" `
    -ReportFile "fighting_specialization_report.json"
exit $LASTEXITCODE
