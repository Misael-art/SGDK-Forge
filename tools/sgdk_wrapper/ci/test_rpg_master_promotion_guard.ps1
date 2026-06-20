$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "test_genre_no_auto_promotion.ps1") `
    -ExpectedId "rpg_turn_based_jrpg" `
    -ValidatorFile "validate_rpg_turn_based_jrpg_specialization.ps1" `
    -ReportFile "rpg_specialization_report.json"
exit $LASTEXITCODE
