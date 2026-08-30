$ErrorActionPreference = "Stop"

$wrapperRoot = Split-Path -Parent $PSScriptRoot
$agentRoot = Join-Path $wrapperRoot ".agent"

function Invoke-Gate {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Action
    )

    Write-Host "RUN  $Label"
    $global:LASTEXITCODE = 0
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "canonical_skill_curation_gate_failed:$($Label):$LASTEXITCODE"
    }
    Write-Host "PASS $Label"
}

$python = Get-Command python -ErrorAction SilentlyContinue
$pythonArgs = @()
if ($null -eq $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
    $pythonArgs = @("-3")
}
if ($null -eq $python) {
    throw "python_runtime_missing"
}

$frameworkValidator = Join-Path $agentRoot "scripts/validate_skill_framework.py"
$videoValidator = Join-Path $wrapperRoot "validate_aaa_video_curation.py"
$lifecycleAuditor = Join-Path $wrapperRoot "audit_skill_lifecycle.ps1"

foreach ($requiredFile in @($frameworkValidator, $videoValidator, $lifecycleAuditor)) {
    if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
        throw "canonical_skill_curation_dependency_missing:$requiredFile"
    }
}

Invoke-Gate -Label "skill framework" -Action {
    & $python.Path @pythonArgs $frameworkValidator
}
Invoke-Gate -Label "skill lifecycle" -Action {
    & $lifecycleAuditor
}
Invoke-Gate -Label "curated route validator" -Action {
    & $python.Path @pythonArgs $videoValidator
}
Invoke-Gate -Label "lifecycle registry tests" -Action {
    & (Join-Path $PSScriptRoot "test_skill_lifecycle_registry.ps1")
}
Invoke-Gate -Label "active routing tests" -Action {
    & (Join-Path $PSScriptRoot "test_active_skill_routing.ps1")
}
Invoke-Gate -Label "Celestial Chase canonical learning" -Action {
    & (Join-Path $PSScriptRoot "test_celestial_chase_canonical_learning.ps1")
}
Invoke-Gate -Label "genre registry tests" -Action {
    & (Join-Path $PSScriptRoot "test_genre_specialization_registry.ps1")
}

foreach ($genre in @(
    "fighting",
    "brawler",
    "platformer",
    "racing",
    "rpg",
    "strategy"
)) {
    Invoke-Gate -Label "$genre specialization" -Action {
        & (Join-Path $PSScriptRoot "test_$($genre)_specialization_registry.ps1")
    }
    Invoke-Gate -Label "$genre orchestrator contract" -Action {
        & (Join-Path $PSScriptRoot "test_$($genre)_specialization_orchestrator.ps1")
    }
}

Write-Host "PASS canonical skill curation integration"
exit 0
