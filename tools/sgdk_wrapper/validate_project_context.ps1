<#
.SYNOPSIS
    Validates the project production context and proportional documentation gates.

.DESCRIPTION
    The context gate decides whether a workspace task is an AAA game, technical
    demo, exercise, game review, or consulting engagement. It prevents two
    failures:
    - demanding full-game documentation for reviews/exercises;
    - letting a real game claim delivery without the required docs.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $false)]
    [ValidateSet('planning', 'implementation', 'closeout', 'release')]
    [string]$Phase = 'planning',

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-Prop {
    param($Object, [string]$Name, $Default = $null)
    if ($null -eq $Object) { return $Default }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) { return $Default }
    return $property.Value
}

function Get-Text {
    param($Value, [string]$Default = '')
    if ($null -eq $Value) { return $Default }
    $text = [string]$Value
    if ([string]::IsNullOrWhiteSpace($text)) { return $Default }
    return $text.Trim()
}

function Read-JsonOrNull {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    try {
        return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Resolve-ProjectPath {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) { return $null }
    if ([System.IO.Path]::IsPathRooted($Value)) {
        return [System.IO.Path]::GetFullPath($Value)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $script:ResolvedProjectRoot $Value))
}

function Test-UnderProject {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
    $full = [System.IO.Path]::GetFullPath($Path)
    $root = $script:ResolvedProjectRoot.TrimEnd('\', '/')
    return $full.Equals($root, [System.StringComparison]::OrdinalIgnoreCase) -or
        $full.StartsWith($root + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)
}

function Test-ProjectFile {
    param([string]$RelativePath)
    $path = Resolve-ProjectPath $RelativePath
    return $path -and (Test-UnderProject $path) -and (Test-Path -LiteralPath $path -PathType Leaf)
}

function Add-Blocker {
    param([string]$Status, [string]$Message, [string]$Path = '', $Details = $null)
    if (-not ($script:Report.blocking_statuses -contains $Status)) {
        $script:Report.blocking_statuses += $Status
    }
    $script:Report.details += [ordered]@{
        level = 'blocking'
        status = $Status
        message = $Message
        path = $Path
        details = $Details
    }
}

function Add-Warning {
    param([string]$Status, [string]$Message, [string]$Path = '', $Details = $null)
    $script:Report.warnings += [ordered]@{
        level = 'warning'
        status = $Status
        message = $Message
        path = $Path
        details = $Details
    }
}

function Require-Docs {
    param([string[]]$Paths, [string]$Reason)
    $missing = @()
    foreach ($path in $Paths) {
        if (-not (Test-ProjectFile $path)) {
            $missing += $path
        }
    }
    if ($missing.Count -gt 0) {
        Add-Blocker 'project_context_required_docs_missing' $Reason $script:ManifestPath @{
            missing = $missing
            phase = $Phase
            context_type = $script:ContextType
        }
    }
}

$script:ResolvedProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
if (-not (Test-Path -LiteralPath $script:ResolvedProjectRoot -PathType Container)) {
    throw "ProjectRoot inexistente: $script:ResolvedProjectRoot"
}
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $script:ResolvedProjectRoot 'out\logs\project_context_report.json'
}

$script:ManifestPath = Join-Path $script:ResolvedProjectRoot 'doc\project_context_manifest.json'
$script:ContextType = 'missing'
$script:Report = [ordered]@{
    schema_version = '1.0.0'
    generated_at = (Get-Date).ToUniversalTime().ToString('o')
    project_root = $script:ResolvedProjectRoot
    phase = $Phase
    manifest_path = $script:ManifestPath
    context_type = $script:ContextType
    documentation_profile = ''
    delivery_claim_ceiling = ''
    status = 'blocked'
    ready = $false
    blocking_statuses = @()
    warnings = @()
    required_documents = @()
    phase_blocking_documents = @()
    non_blocking_documents = @()
    details = @()
}

$contextRules = @{
    aaa_game = @{
        profile = 'full_game'
        ceilings = @('vertical_slice', 'ready_for_aaa', 'release_candidate')
        required = @(
            'doc/project_context_manifest.json',
            'doc/00-project-brief.md',
            'doc/11-gdd.md',
            'doc/15-tdd.md',
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
        phase = @(
            'doc/16-ldd.md',
            'doc/17-audio-design.md',
            'doc/20-release-marketing-legal.md'
        )
    }
    technical_demo = @{
        profile = 'demo'
        ceilings = @('lab', 'prototype', 'technical_demo')
        required = @(
            'doc/project_context_manifest.json',
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
        phase = @('doc/15-tdd.md')
    }
    exercise = @{
        profile = 'exercise'
        ceilings = @('exercise', 'prototype')
        required = @(
            'doc/project_context_manifest.json',
            'doc/00-project-brief.md',
            'doc/project_methodology_manifest.json',
            'doc/project_hygiene_manifest.json',
            'doc/10-memory-bank.md',
            'doc/changelog/changelog.md',
            'doc/agent_learning/learning_ledger.json'
        )
        phase = @('doc/technique_usage_manifest.json')
    }
    game_review = @{
        profile = 'review'
        ceilings = @('none', 'concept')
        required = @(
            'doc/project_context_manifest.json',
            'doc/21-review-consulting-context.md',
            'doc/10-memory-bank.md'
        )
        phase = @()
    }
    consulting = @{
        profile = 'consulting'
        ceilings = @('none', 'concept')
        required = @(
            'doc/project_context_manifest.json',
            'doc/21-review-consulting-context.md',
            'doc/10-memory-bank.md'
        )
        phase = @()
    }
}

$manifest = Read-JsonOrNull $script:ManifestPath
if (-not (Test-Path -LiteralPath $script:ManifestPath -PathType Leaf)) {
    Add-Blocker 'project_context_manifest_missing' 'Projeto sem doc/project_context_manifest.json; classifique o contexto antes de abrir producao.' $script:ManifestPath
} elseif ($null -eq $manifest) {
    Add-Blocker 'project_context_manifest_invalid_json' 'doc/project_context_manifest.json possui JSON invalido.' $script:ManifestPath
} else {
    $script:ContextType = Get-Text (Get-Prop $manifest 'context_type' '')
    $profile = Get-Text (Get-Prop $manifest 'documentation_profile' '')
    $ceiling = Get-Text (Get-Prop $manifest 'delivery_claim_ceiling' '')
    $status = Get-Text (Get-Prop $manifest 'context_status' '')
    $script:Report.context_type = $script:ContextType
    $script:Report.documentation_profile = $profile
    $script:Report.delivery_claim_ceiling = $ceiling

    if ($script:ContextType -eq 'unclassified' -or [string]::IsNullOrWhiteSpace($script:ContextType)) {
        Add-Blocker 'project_context_unclassified' 'Classifique o contexto: aaa_game, technical_demo, exercise, game_review ou consulting.' $script:ManifestPath
    } elseif (-not $contextRules.ContainsKey($script:ContextType)) {
        Add-Blocker 'project_context_invalid' 'context_type desconhecido.' $script:ManifestPath @{
            context_type = $script:ContextType
        }
    } else {
        $rule = $contextRules[$script:ContextType]
        $script:Report.required_documents = $rule.required
        $script:Report.phase_blocking_documents = $rule.phase

        if ($profile -ne $rule.profile) {
            Add-Blocker 'project_context_profile_mismatch' 'documentation_profile nao combina com context_type.' $script:ManifestPath @{
                context_type = $script:ContextType
                expected_profile = $rule.profile
                actual_profile = $profile
            }
        }
        if ($rule.ceilings -notcontains $ceiling) {
            Add-Blocker 'project_context_claim_ceiling_invalid' 'delivery_claim_ceiling excede ou contradiz o contexto.' $script:ManifestPath @{
                context_type = $script:ContextType
                allowed = $rule.ceilings
                actual = $ceiling
            }
        }
        if ($status -eq 'unclassified' -or [string]::IsNullOrWhiteSpace($status)) {
            Add-Blocker 'project_context_status_unclassified' 'context_status precisa refletir o estado real da sessao.' $script:ManifestPath
        }

        $decision = Get-Prop $manifest 'context_decision_record' $null
        $selectedBy = Get-Text (Get-Prop $decision 'selected_by' '')
        $rationale = Get-Text (Get-Prop $decision 'rationale' '')
        $requiresHuman = [bool](Get-Prop $decision 'human_confirmation_required_for_mode_change' $false)
        if ($selectedBy -eq 'unselected' -or $rationale.Length -lt 8 -or -not $requiresHuman) {
            Add-Blocker 'project_context_decision_record_invalid' 'context_decision_record precisa explicar a escolha e preservar confirmacao humana para troca de modo.' $script:ManifestPath
        }

        Require-Docs $rule.required 'Documentos bloqueantes ausentes para o contexto selecionado.'
        if ($script:ContextType -eq 'aaa_game' -and $Phase -in @('implementation', 'closeout', 'release')) {
            Require-Docs @('doc/16-ldd.md', 'doc/17-audio-design.md') 'Jogo AAA em implementacao/closeout precisa de LDD e Audio Design proporcionais.'
        }
        if ($script:ContextType -eq 'aaa_game' -and $Phase -eq 'release') {
            Require-Docs @('doc/20-release-marketing-legal.md') 'Release publico precisa de checklist de release, marketing e legal.'
        }
        if ($script:ContextType -eq 'technical_demo' -and $Phase -in @('closeout', 'release')) {
            Require-Docs @('doc/15-tdd.md') 'Demo tecnica em closeout precisa registrar a solucao tecnica executavel.'
        }

        $allKnownDocs = @(
            'doc/00-project-brief.md',
            'doc/11-gdd.md',
            'doc/15-tdd.md',
            'doc/13-spec-cenas.md',
            'doc/14-plano-de-provas-qa.md',
            'doc/16-ldd.md',
            'doc/17-audio-design.md',
            'doc/18-asset-register.json',
            'doc/19-roadmap-risk-register.md',
            'doc/20-release-marketing-legal.md',
            'doc/21-review-consulting-context.md'
        )
        $blockingNow = @($rule.required)
        if ($script:ContextType -eq 'aaa_game' -and $Phase -in @('implementation', 'closeout')) {
            $blockingNow += @('doc/16-ldd.md', 'doc/17-audio-design.md')
        }
        if ($script:ContextType -eq 'aaa_game' -and $Phase -eq 'release') {
            $blockingNow += @('doc/16-ldd.md', 'doc/17-audio-design.md', 'doc/20-release-marketing-legal.md')
        }
        if ($script:ContextType -eq 'technical_demo' -and $Phase -in @('closeout', 'release')) {
            $blockingNow += @('doc/15-tdd.md')
        }
        $script:Report.non_blocking_documents = @($allKnownDocs | Where-Object { $blockingNow -notcontains $_ })

        $policy = Get-Prop $manifest 'blocking_policy' $null
        $docs = @((Get-Prop $policy 'documents' @()))
        foreach ($doc in $docs) {
            $path = Get-Text (Get-Prop $doc 'path' '')
            if ([System.IO.Path]::IsPathRooted($path)) {
                Add-Blocker 'project_context_absolute_doc_path' 'blocking_policy.documents deve usar caminhos relativos ao projeto.' $script:ManifestPath @{
                    path = $path
                }
            }
        }

        $manifestDeclaredRequired = @(
            $docs |
                Where-Object { @((Get-Prop $_ 'required_for_contexts' @())) -contains $script:ContextType } |
                ForEach-Object { Get-Text (Get-Prop $_ 'path' '') } |
                Where-Object { $_ }
        )
        foreach ($requiredPath in $rule.required) {
            if ($manifestDeclaredRequired -notcontains $requiredPath) {
                Add-Warning 'project_context_policy_incomplete' 'Manifest nao declara um documento que o validador considera bloqueante para este contexto.' $script:ManifestPath @{
                    missing_policy_path = $requiredPath
                    context_type = $script:ContextType
                }
            }
        }
    }
}

$script:Report.ready = ($script:Report.blocking_statuses.Count -eq 0)
$script:Report.status = if ($script:Report.ready) { 'passed' } else { 'blocked' }

$outputParent = Split-Path $OutputPath -Parent
if (-not (Test-Path -LiteralPath $outputParent -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $outputParent | Out-Null
}
[System.IO.File]::WriteAllText(
    $OutputPath,
    ($script:Report | ConvertTo-Json -Depth 20),
    [System.Text.Encoding]::UTF8
)

Write-Host ("[validate_project_context] status={0} context={1} phase={2} blockers={3} report={4}" -f $script:Report.status, $script:Report.context_type, $Phase, $script:Report.blocking_statuses.Count, $OutputPath)
if ($script:Report.ready) { exit 0 }
exit 1
