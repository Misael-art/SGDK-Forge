<#
.SYNOPSIS
    Verifies the racing-sports-adventure-game-design orchestrator skill is a thin delegator.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$skillRoot = Join-Path $wrapperRoot '.agent\skills\planning\racing-sports-adventure-game-design'
$skillMd = Join-Path $skillRoot 'SKILL.md'
$openaiYaml = Join-Path $skillRoot 'agents\openai.yaml'
$lexicon = Join-Path $skillRoot 'references\racing_design_lexicon.md'
$orchestratorMap = Join-Path $skillRoot 'references\racing_orchestrator_map.md'

$passed = 0
$failed = 0
$total = 0

function Assert-True {
    param([string]$Name, [bool]$Condition, [string]$Detail = '')
    $script:total++
    if ($Condition) {
        $script:passed++
        Write-Host "  [PASS] $Name"
    } else {
        $script:failed++
        $msg = "  [FAIL] $Name"
        if ($Detail) { $msg += " -- $Detail" }
        Write-Host $msg
    }
}

Write-Host ''
Write-Host '=== Racing Specialization Orchestrator Test ==='
Write-Host ''

Assert-True 'SKILL.md present' (Test-Path -LiteralPath $skillMd) $skillMd
Assert-True 'agents/openai.yaml present' (Test-Path -LiteralPath $openaiYaml) $openaiYaml
Assert-True 'references/racing_design_lexicon.md present' (Test-Path -LiteralPath $lexicon) $lexicon
Assert-True 'references/racing_orchestrator_map.md present' (Test-Path -LiteralPath $orchestratorMap) $orchestratorMap

if (-not (Test-Path -LiteralPath $openaiYaml)) { Write-Host ''; Write-Host "=== Results: $passed/$total passed, $failed failed ==="; exit 1 }

$yaml = Get-Content -LiteralPath $openaiYaml -Raw -Encoding UTF8
Assert-True 'allow_implicit_invocation=false' ($yaml -match 'allow_implicit_invocation:\s*false') ('not found')
Assert-True 'default_prompt mentions racing_arcade' ($yaml -match 'racing_arcade') ('not found')
Assert-True 'default_prompt forbids folder-name inference' ($yaml -match 'NUNCA infere') ('not found')
Assert-True 'default_prompt references canonical validator' ($yaml -match 'validate_racing_arcade_specialization\.ps1') ('not found')

$skillContent = Get-Content -LiteralPath $skillMd -Raw -Encoding UTF8
$skillLineCount = ($skillContent -split "`n").Count
Assert-True 'SKILL.md is thin (lines <= 220)' ($skillLineCount -le 220) ("$skillLineCount lines")
Assert-True 'SKILL.md references all 3 racing schemas' (($skillContent -match 'racing_arcade_design_contract\.schema\.json') -and ($skillContent -match 'racing_vehicle_frame_data\.schema\.json') -and ($skillContent -match 'racing_specialization_report\.schema\.json')) ('missing schema reference')
Assert-True 'SKILL.md forbids name/keyword/regex inference' (($skillContent -match 'NOME de pasta') -and ($skillContent -match 'regex')) ('not explicit')
Assert-True 'SKILL.md pins time_unit=frames' ($skillContent -match 'time_unit\s*=\s*"frames"') ('not explicit')
Assert-True 'SKILL.md pins camera=behind_or_chase' ($skillContent -match 'camera.*behind_or_chase' -or $skillContent -match 'camera\s*=.*behind') ('not explicit')
Assert-True 'SKILL.md pins track_count_max=16' ($skillContent -match 'track_count_max\s*=\s*16') ('not explicit')
Assert-True 'SKILL.md pins lap_count_max=5' ($skillContent -match 'lap_count_max\s*=\s*5') ('not explicit')
Assert-True 'SKILL.md pins boost_on_drift=on' ($skillContent -match 'boost_on_drift\s*=\s*"on"') ('not explicit')
Assert-True 'SKILL.md pins collision_model=arcade_forgiving' (($skillContent -match 'collision_model\s*=\s*"arcade_forgiving"') -or ($skillContent -match 'collision_model.*arcade_forgiving')) ('not explicit')

$map = Get-Content -LiteralPath $orchestratorMap -Raw -Encoding UTF8
Assert-True 'orchestrator map mentions systems-mechanics-validator' ($map -match 'systems-mechanics-validator') ('not found')
Assert-True 'orchestrator map mentions character-design' ($map -match 'character-design') ('not found')
Assert-True 'orchestrator map mentions sprite-animation' ($map -match 'sprite-animation') ('not found')
Assert-True 'orchestrator map mentions megadrive-vdp-budget-analyst' ($map -match 'megadrive-vdp-budget-analyst') ('not found')
Assert-True 'orchestrator map mentions xgm2-audio-director' ($map -match 'xgm2-audio-director') ('not found')
Assert-True 'orchestrator map mentions sgdk-runtime-coder' ($map -match 'sgdk-runtime-coder') ('not found')
Assert-True 'orchestrator map mentions tdd-authoring' ($map -match 'tdd-authoring') ('not found')

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
