<#
.SYNOPSIS
    Verifies the brawler-game-design orchestrator skill is a thin
    delegator: SKILL.md present, agents/openai.yaml has
    allow_implicit_invocation=false, references are listed and reachable.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$skillRoot = Join-Path $wrapperRoot '.agent\skills\planning\brawler-game-design'
$skillMd = Join-Path $skillRoot 'SKILL.md'
$openaiYaml = Join-Path $skillRoot 'agents\openai.yaml'
$lexicon = Join-Path $skillRoot 'references\brawler_design_lexicon.md'
$orchestratorMap = Join-Path $skillRoot 'references\brawler_orchestrator_map.md'

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
Write-Host '=== Brawler Specialization Orchestrator Test ==='
Write-Host ''

Assert-True 'SKILL.md present' (Test-Path -LiteralPath $skillMd) $skillMd
Assert-True 'agents/openai.yaml present' (Test-Path -LiteralPath $openaiYaml) $openaiYaml
Assert-True 'references/brawler_design_lexicon.md present' (Test-Path -LiteralPath $lexicon) $lexicon
Assert-True 'references/brawler_orchestrator_map.md present' (Test-Path -LiteralPath $orchestratorMap) $orchestratorMap

if (-not (Test-Path -LiteralPath $openaiYaml)) { Write-Host ''; Write-Host "=== Results: $passed/$total passed, $failed failed ==="; exit 1 }

$yaml = Get-Content -LiteralPath $openaiYaml -Raw -Encoding UTF8
Assert-True 'allow_implicit_invocation=false' ($yaml -match 'allow_implicit_invocation:\s*false') ('not found')
Assert-True 'default_prompt mentions brawler_belt_scroll' ($yaml -match 'brawler_belt_scroll') ('not found')
Assert-True 'default_prompt forbids folder-name inference' ($yaml -match 'NUNCA infere') ('not found')
Assert-True 'default_prompt references canonical validator' ($yaml -match 'validate_brawler_belt_scroll_specialization\.ps1') ('not found')

$skillContent = Get-Content -LiteralPath $skillMd -Raw -Encoding UTF8
$skillLineCount = ($skillContent -split "`n").Count
Assert-True 'SKILL.md is thin (lines <= 220)' ($skillLineCount -le 220) ("$skillLineCount lines")
Assert-True 'SKILL.md references all 3 brawler schemas' (($skillContent -match 'brawler_belt_scroll_design_contract\.schema\.json') -and ($skillContent -match 'brawler_enemy_archetype_frame_data\.schema\.json') -and ($skillContent -match 'brawler_specialization_report\.schema\.json')) ('missing schema reference')
Assert-True 'SKILL.md forbids name/keyword/regex inference' (($skillContent -match 'NOME de pasta') -and ($skillContent -match 'regex')) ('not explicit')
Assert-True 'SKILL.md pins time_unit=frames' ($skillContent -match 'time_unit\s*=\s*"frames"') ('not explicit')
Assert-True 'SKILL.md pins camera=horizontal_lanes' ($skillContent -match 'camera\s*=\s*"horizontal_lanes"') ('not explicit')
Assert-True 'SKILL.md pins enemy_count_on_screen_max=8' ($skillContent -match 'enemy_count_on_screen_max\s*=\s*8') ('not explicit')
Assert-True 'SKILL.md pins stage_progression=linear_with_bosses' ($skillContent -match 'stage_progression\s*=\s*"linear_with_bosses"') ('not explicit')
Assert-True 'SKILL.md pins iframe_on_hit=on' ($skillContent -match 'iframe_on_hit\s*=\s*"on"') ('not explicit')

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
