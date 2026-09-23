<#
.SYNOPSIS
    Regression suite for project-local technique evidence and document references.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$workspaceRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$validator = Join-Path $wrapperRoot 'validate_resources.ps1'
$modelRoot = Join-Path $wrapperRoot 'modelo'
$fixtureRoot = Join-Path $workspaceRoot 'out\ci\technique_usage_fixture'
$reportPath = Join-Path $fixtureRoot 'out\logs\validation_report.json'

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
        Write-Host "  [FAIL] $Name -- $Detail"
    }
}

function Write-JsonFile {
    param([string]$Path, $Value)
    $parent = Split-Path $Path -Parent
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    [System.IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 20), [System.Text.Encoding]::UTF8)
}

function Reset-Fixture {
    if (Test-Path -LiteralPath $fixtureRoot) {
        Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
    }
    foreach ($relative in @('doc', 'doc\changelog', 'src', 'res', 'out\logs', 'rascunho', '.mddev')) {
        New-Item -ItemType Directory -Force -Path (Join-Path $fixtureRoot $relative) | Out-Null
    }
    foreach ($relative in @(
        'doc\03-arquitetura.md',
        'doc\10-memory-bank.md',
        'doc\11-gdd.md',
        'doc\13-spec-cenas.md',
        'doc\changelog\changelog.md',
        'doc\project_methodology_manifest.json',
        'doc\project_hygiene_manifest.json'
    )) {
        Copy-Item -LiteralPath (Join-Path $modelRoot $relative) -Destination (Join-Path $fixtureRoot $relative) -Force
    }
}

function New-TechniqueManifest {
    param(
        [string[]]$DocRefs,
        $AllowedExternal = @(),
        [string]$BudgetPath = ''
    )
    return [ordered]@{
        schema_version = '1.0.0'
        project = [ordered]@{
            name = 'Technique Usage Fixture [VER.999] [SGDK 211] [GEN] [LAB] [TECHDEMO]'
            project_root_policy = 'all_project_material_inside_project'
            lab_not_delivery = $true
        }
        registry_source = 'doc/05_technical/93_16bit_hardware_mastery_registry.json'
        documentation_sync = [ordered]@{
            doc_13_spec_cenas = $true
            doc_10_memory_bank = $true
            doc_changelog = $true
        }
        allowed_external_artifacts = $AllowedExternal
        techniques = @(
            [ordered]@{
                scene_id = 'fixture_scene'
                registry_id = 'line_scrolling'
                human_proficiency_status = 'TEORICA_PRIORITARIA'
                technique_tags = @('LINE_SCROLL', 'PARALLAX')
                owner_skills = @('sgdk-runtime-coder', 'megadrive-vdp-budget-analyst')
                evidence = [ordered]@{
                    blastem_evidence_paths = @()
                    budget_report_path = if ($BudgetPath) { $BudgetPath } else { $null }
                    validation_report_path = $null
                    promotion_record_path = $null
                }
                doc_refs = $DocRefs
            }
        )
    }
}

function Invoke-Validator {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $validator -WorkDir $fixtureRoot | Out-Null
    return Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
}

Write-Host ''
Write-Host '=== Technique Usage Governance Test ==='
Write-Host ''

try {
    Reset-Fixture
    Write-JsonFile (Join-Path $fixtureRoot 'doc\technique_usage_manifest.json') (
        New-TechniqueManifest `
            -DocRefs @('doc/13-spec-cenas.md', 'doc/10-memory-bank.md', 'doc/changelog/changelog.md') `
            -AllowedExternal @(@{ path = 'C:/outside/budget.json'; reason = 'legacy'; human_authorized = $true }) `
            -BudgetPath 'C:/outside/budget.json'
    )
    $report = Invoke-Validator
    Assert-True 'external authorization no longer permits outside evidence' (@($report.blocking_statuses) -contains 'technique_evidence_outside_project') (@($report.blocking_statuses) -join ',')

    Reset-Fixture
    Write-JsonFile (Join-Path $fixtureRoot 'doc\technique_usage_manifest.json') (
        New-TechniqueManifest -DocRefs @('doc/13-spec-cenas.md')
    )
    $report = Invoke-Validator
    Assert-True 'missing local memory/changelog refs block technique sync' (@($report.blocking_statuses) -contains 'technique_documentation_sync_missing') (@($report.blocking_statuses) -join ',')

    Reset-Fixture
    Write-JsonFile (Join-Path $fixtureRoot 'doc\technique_usage_manifest.json') (
        New-TechniqueManifest -DocRefs @('doc/13-spec-cenas.md', 'doc/10-memory-bank.md', 'doc/changelog/changelog.md')
    )
    $report = Invoke-Validator
    $techniqueSpecific = @($report.blocking_statuses | Where-Object {
        $_ -in @('technique_evidence_outside_project', 'technique_documentation_sync_missing', 'technique_registry_id_unknown', 'technique_tag_unknown')
    })
    Assert-True 'local coherent technique manifest avoids technique-specific blockers' ($techniqueSpecific.Count -eq 0) ($techniqueSpecific -join ',')
} finally {
    if (Test-Path -LiteralPath $fixtureRoot) {
        Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
    }
}

Write-Host ''
Write-Host ("=== Results: {0}/{1} passed, {2} failed ===" -f $script:passed, $script:total, $script:failed)
if ($script:failed -gt 0) { exit 1 }
exit 0
