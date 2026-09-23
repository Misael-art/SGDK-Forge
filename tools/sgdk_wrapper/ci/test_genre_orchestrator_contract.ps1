<#
.SYNOPSIS
    Shared contract test for explicit opt-in genre orchestrators.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$SkillId,
    [Parameter(Mandatory = $true)][string]$SpecializationId
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$WrapperRoot = Split-Path $PSScriptRoot -Parent
$SkillRoot = Join-Path $WrapperRoot ".agent\skills\planning\$SkillId"
$SkillPath = Join-Path $SkillRoot "SKILL.md"
$YamlPath = Join-Path $SkillRoot "agents\openai.yaml"

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

Assert-True (Test-Path -LiteralPath $SkillPath -PathType Leaf) "SKILL.md missing: $SkillId"
Assert-True (Test-Path -LiteralPath $YamlPath -PathType Leaf) "openai.yaml missing: $SkillId"

$skill = Get-Content -LiteralPath $SkillPath -Raw -Encoding UTF8
$yaml = Get-Content -LiteralPath $YamlPath -Raw -Encoding UTF8
$wordCount = [regex]::Matches($skill, "\S+").Count

Assert-True ($wordCount -le 550) "orchestrator exceeds 550 words: $SkillId ($wordCount)"
Assert-True ($skill -match [regex]::Escape($SpecializationId)) "implemented specialization missing: $SkillId"
Assert-True ($skill -match "(?i)Entrada minima") "Entrada minima missing: $SkillId"
Assert-True ($skill -match "(?i)Saida minima") "Saida minima missing: $SkillId"
Assert-True ($skill -match "(?i)Passa quando") "Passa quando missing: $SkillId"
Assert-True ($skill -match "(?i)Handoff") "Handoff missing: $SkillId"
Assert-True ($skill -match "(?i)opt-in|opt.in") "explicit opt-in missing: $SkillId"
Assert-True ($yaml -match "allow_implicit_invocation:\s*false") "implicit invocation must be false: $SkillId"
Assert-True ($yaml -match [regex]::Escape("`$$SkillId")) "default prompt must mention skill token: $SkillId"

foreach ($forbidden in @(
    "Party size maximo",
    "Stage count:",
    "Track count:",
    "Wave count maximo",
    "Level count:",
    "Magias distintas:",
    "Inventario: 8-12"
)) {
    Assert-True ($skill -notmatch [regex]::Escape($forbidden)) "unsupported hard ceiling remains in $SkillId`: $forbidden"
}

Write-Host "[PASS] $SkillId is a thin explicit orchestrator for $SpecializationId"
exit 0
