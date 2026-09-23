$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "test_genre_no_auto_promotion.ps1") `
    -ExpectedId "strategy_tower_defense" `
    -ValidatorFile "validate_strategy_tower_defense_specialization.ps1" `
    -ReportFile "strategy_specialization_report.json"
exit $LASTEXITCODE
