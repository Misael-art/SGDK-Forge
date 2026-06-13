<#
.SYNOPSIS
    Regression suite for project context classification and proportional docs.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$validator = Join-Path $wrapperRoot 'validate_project_context.ps1'
$templateManifestPath = Join-Path $wrapperRoot 'modelo\doc\project_context_manifest.json'
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\project_context_governance_fixture'
$reportPath = Join-Path $fixtureRoot 'out\logs\project_context_report.json'

$script:passed = 0
$script:failed = 0
$script:total = 0

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

function Reset-Fixture {
    if (Test-Path -LiteralPath $fixtureRoot) {
        Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\changelog') | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'doc\agent_learning') | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot 'out\logs') | Out-Null
}

function Write-TextFile {
    param([string]$RelativePath, [string]$Content = 'fixture')
    $path = Join-Path $fixtureRoot $RelativePath
    $parent = Split-Path $path -Parent
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    [System.IO.File]::WriteAllText($path, $Content, [System.Text.Encoding]::UTF8)
}

function Write-JsonFile {
    param([string]$RelativePath, $Value)
    $path = Join-Path $fixtureRoot $RelativePath
    $parent = Split-Path $path -Parent
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    [System.IO.File]::WriteAllText($path, ($Value | ConvertTo-Json -Depth 20), [System.Text.Encoding]::UTF8)
}

function New-ContextManifest {
    param(
        [string]$ContextType,
        [string]$Profile,
        [string]$Ceiling,
        [string]$Status = 'planned'
    )
    $manifest = Get-Content -LiteralPath $templateManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $manifest.context_type = $ContextType
    $manifest.documentation_profile = $Profile
    $manifest.delivery_claim_ceiling = $Ceiling
    $manifest.context_status = $Status
    $manifest.context_decision_record.selected_by = 'human'
    $manifest.context_decision_record.rationale = 'Human selected the test context for this fixture.'
    $manifest.context_decision_record.evidence_or_prompt = 'test fixture'
    $manifest.context_decision_record.human_confirmation_required_for_mode_change = $true
    return $manifest
}

function Invoke-ContextValidator {
    param([string]$Phase = 'planning')
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $validator `
        -ProjectRoot $fixtureRoot `
        -Phase $Phase `
        -OutputPath $reportPath | Out-Null
    $exitCode = $LASTEXITCODE
    $report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
    return [pscustomobject]@{
        exit_code = $exitCode
        report = $report
        statuses = @($report.blocking_statuses)
    }
}

function Has-Status {
    param($Run, [string]$Status)
    return @($Run.statuses) -contains $Status
}

function Write-BaseDocs {
    param([string[]]$Paths)
    foreach ($path in $Paths) {
        if ($path.EndsWith('.json')) {
            Write-JsonFile $path @{ fixture = $true }
        } else {
            Write-TextFile $path '# fixture'
        }
    }
}

Write-Host ''
Write-Host '=== Project Context Governance Test ==='
Write-Host ''

try {
    Reset-Fixture
    $run = Invoke-ContextValidator
    Assert-True 'missing project_context_manifest blocks opening' (Has-Status $run 'project_context_manifest_missing')

    Reset-Fixture
    Copy-Item -LiteralPath $templateManifestPath -Destination (Join-Path $fixtureRoot 'doc\project_context_manifest.json')
    $run = Invoke-ContextValidator
    Assert-True 'unclassified context blocks production' (Has-Status $run 'project_context_unclassified')

    Reset-Fixture
    Write-JsonFile 'doc/project_context_manifest.json' (New-ContextManifest -ContextType 'aaa_game' -Profile 'full_game' -Ceiling 'vertical_slice')
    Write-BaseDocs @(
        'doc/00-project-brief.md',
        'doc/11-gdd.md',
        'doc/13-spec-cenas.md',
        'doc/14-plano-de-provas-qa.md',
        'doc/18-asset-register.json',
        'doc/19-roadmap-risk-register.md',
        'doc/project_methodology_manifest.json',
        'doc/project_hygiene_manifest.json',
        'doc/technique_usage_manifest.json',
        'doc/10-memory-bank.md',
        'doc/changelog/changelog.md'
    )
    $run = Invoke-ContextValidator
    Assert-True 'AAA game without TDD blocks planning' (Has-Status $run 'project_context_required_docs_missing')

    Write-TextFile 'doc/15-tdd.md' '# TDD'
    $run = Invoke-ContextValidator
    Assert-True 'AAA game planning passes with required docs' ($run.exit_code -eq 0) ($run.statuses -join ',')

    $run = Invoke-ContextValidator -Phase implementation
    Assert-True 'AAA game implementation needs LDD/audio design' (Has-Status $run 'project_context_required_docs_missing')
    Write-TextFile 'doc/16-ldd.md' '# LDD'
    Write-TextFile 'doc/17-audio-design.md' '# Audio'
    $run = Invoke-ContextValidator -Phase implementation
    Assert-True 'AAA game implementation passes with phase docs' ($run.exit_code -eq 0) ($run.statuses -join ',')

    Reset-Fixture
    Write-JsonFile 'doc/project_context_manifest.json' (New-ContextManifest -ContextType 'technical_demo' -Profile 'demo' -Ceiling 'technical_demo')
    Write-BaseDocs @(
        'doc/00-project-brief.md',
        'doc/13-spec-cenas.md',
        'doc/14-plano-de-provas-qa.md',
        'doc/18-asset-register.json',
        'doc/project_methodology_manifest.json',
        'doc/project_hygiene_manifest.json',
        'doc/technique_usage_manifest.json',
        'doc/10-memory-bank.md',
        'doc/changelog/changelog.md'
    )
    $run = Invoke-ContextValidator
    Assert-True 'technical demo does not require full GDD/TDD during planning' ($run.exit_code -eq 0) ($run.statuses -join ',')
    $run = Invoke-ContextValidator -Phase closeout
    Assert-True 'technical demo closeout needs TDD record' (Has-Status $run 'project_context_required_docs_missing')

    Reset-Fixture
    Write-JsonFile 'doc/project_context_manifest.json' (New-ContextManifest -ContextType 'consulting' -Profile 'consulting' -Ceiling 'concept' -Status 'consultive')
    Write-BaseDocs @(
        'doc/21-review-consulting-context.md',
        'doc/10-memory-bank.md'
    )
    $run = Invoke-ContextValidator
    Assert-True 'consulting context does not require ROM, GDD, scene spec, or QA' ($run.exit_code -eq 0) ($run.statuses -join ',')

    Reset-Fixture
    Write-JsonFile 'doc/project_context_manifest.json' (New-ContextManifest -ContextType 'exercise' -Profile 'exercise' -Ceiling 'ready_for_aaa')
    Write-BaseDocs @(
        'doc/00-project-brief.md',
        'doc/project_methodology_manifest.json',
        'doc/project_hygiene_manifest.json',
        'doc/10-memory-bank.md',
        'doc/changelog/changelog.md',
        'doc/agent_learning/learning_ledger.json'
    )
    $run = Invoke-ContextValidator
    Assert-True 'exercise cannot claim ready_for_aaa ceiling' (Has-Status $run 'project_context_claim_ceiling_invalid')
}
finally {
    if (Test-Path -LiteralPath $fixtureRoot) {
        Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
    }
}

Write-Host ''
Write-Host "=== Results: $($script:passed)/$($script:total) passed, $($script:failed) failed ==="
if ($script:failed -gt 0) { exit 1 }
exit 0
