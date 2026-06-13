<#
.SYNOPSIS
    Verifies the rpg-game-design orchestrator skill is a thin
    delegator: SKILL.md present, agents/openai.yaml has
    allow_implicit_invocation=false, references are listed and reachable.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$skillRoot = Join-Path $wrapperRoot '.agent\skills\planning\rpg-game-design'
$skillMd = Join-Path $skillRoot 'SKILL.md'
$openaiYaml = Join-Path $skillRoot 'agents\openai.yaml'
$lexicon = Join-Path $skillRoot 'references\rpg_design_lexicon.md'
$orchestratorMap = Join-Path $skillRoot 'references\rpg_orchestrator_map.md'

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
Write-Host '=== RPG Specialization Orchestrator Test ==='
Write-Host ''

Assert-True 'SKILL.md present' (Test-Path -LiteralPath $skillMd) $skillMd
Assert-True 'agents/openai.yaml present' (Test-Path -LiteralPath $openaiYaml) $openaiYaml
Assert-True 'references/rpg_design_lexicon.md present' (Test-Path -LiteralPath $lexicon) $lexicon
Assert-True 'references/rpg_orchestrator_map.md present' (Test-Path -LiteralPath $orchestratorMap) $orchestratorMap

if (-not (Test-Path -LiteralPath $openaiYaml)) { Write-Host ''; Write-Host "=== Results: $passed/$total passed, $failed failed ==="; exit 1 }

$yaml = Get-Content -LiteralPath $openaiYaml -Raw -Encoding UTF8
Assert-True 'allow_implicit_invocation=false' ($yaml -match 'allow_implicit_invocation:\s*false') ('not found')
Assert-True 'default_prompt mentions rpg_turn_based_jrpg' ($yaml -match 'rpg_turn_based_jrpg') ('not found')
Assert-True 'default_prompt forbids folder-name inference' ($yaml -match 'NUNCA infere') ('not found')
Assert-True 'default_prompt references canonical validator' ($yaml -match 'validate_rpg_turn_based_jrpg_specialization\.ps1') ('not found')

# SKILL.md is thin (no schema bodies, no monsters)
$skillContent = Get-Content -LiteralPath $skillMd -Raw -Encoding UTF8
$skillLineCount = ($skillContent -split "`n").Count
Assert-True 'SKILL.md is thin (lines <= 200)' ($skillLineCount -le 200) ("$skillLineCount lines")
Assert-True 'SKILL.md references all 4 RPG schemas' (($skillContent -match 'rpg_turn_based_jrpg_design_contract\.schema\.json') -and ($skillContent -match 'rpg_party_frame_data\.schema\.json') -and ($skillContent -match 'rpg_specialization_report\.schema\.json') -and ($skillContent -match 'genre_specialization_manifest\.schema\.json')) ('missing schema reference')
Assert-True 'SKILL.md forbids name/keyword/regex inference' (($skillContent -match 'NOME de pasta') -and ($skillContent -match 'regex')) ('not explicit')
Assert-True 'SKILL.md pins time_unit=ticks (turn)' ($skillContent -match 'time_unit\s*=\s*"ticks \(turn\)"') ('not explicit')
Assert-True 'SKILL.md pins party_size_max=4' ($skillContent -match 'party_size_max\s*=\s*4') ('not explicit')
Assert-True 'SKILL.md pins permadeath=off' ($skillContent -match 'permadeath\s*=\s*"off"') ('not explicit')

# Orchestrator map
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
