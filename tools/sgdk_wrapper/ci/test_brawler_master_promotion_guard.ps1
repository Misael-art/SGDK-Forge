$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "test_genre_no_auto_promotion.ps1") `
    -ExpectedId "brawler_belt_scroll" `
    -ValidatorFile "validate_brawler_belt_scroll_specialization.ps1" `
    -ReportFile "brawler_specialization_report.json"
exit $LASTEXITCODE
