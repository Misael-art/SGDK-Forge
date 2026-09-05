<#
.SYNOPSIS
    Materializes missing project-local methodology manifests without overwrite.

.DESCRIPTION
    Safe for old and new projects:
    - creates files only when absent
    - keeps every artifact inside the project
    - leaves claims as review_required until explicitly classified
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $false)]
    [ValidateSet('new', 'existing', 'reseed')]
    [string]$Lifecycle = 'existing',

    [Parameter(Mandatory = $false)]
    [string]$ProjectName = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-JsonUtf8 {
    param([string]$Path, $Value)
    $parent = Split-Path $Path -Parent
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    [System.IO.File]::WriteAllText(
        $Path,
        ($Value | ConvertTo-Json -Depth 20),
        [System.Text.Encoding]::UTF8
    )
}

function Resolve-PowerShellHost {
    foreach ($candidate in @('pwsh', 'powershell', 'powershell.exe')) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($null -ne $command) {
            return $command.Source
        }
    }
    throw 'Nenhum host PowerShell encontrado (pwsh/powershell/powershell.exe).'
}

$resolvedProject = [System.IO.Path]::GetFullPath($ProjectRoot)
if (-not (Test-Path -LiteralPath $resolvedProject -PathType Container)) {
    throw "ProjectRoot inexistente: $resolvedProject"
}

$manifestProjectPath = Join-Path $resolvedProject '.mddev\project.json'
$projectManifest = $null
if (Test-Path -LiteralPath $manifestProjectPath -PathType Leaf) {
    try {
        $projectManifest = Get-Content -LiteralPath $manifestProjectPath -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
        $projectManifest = $null
    }
}

if ([string]::IsNullOrWhiteSpace($ProjectName)) {
    if ($projectManifest -and $projectManifest.PSObject.Properties['display_name'] -and $projectManifest.display_name) {
        $ProjectName = [string]$projectManifest.display_name
    } elseif ($projectManifest -and $projectManifest.PSObject.Properties['name'] -and $projectManifest.name) {
        $ProjectName = [string]$projectManifest.name
    } else {
        $ProjectName = Split-Path $resolvedProject -Leaf
    }
}
if ([string]::IsNullOrWhiteSpace($ProjectName) -or $ProjectName -eq '__PROJECT_NAME__') {
    $ProjectName = Split-Path $resolvedProject -Leaf
}

$methodologyTemplatePath = Join-Path $PSScriptRoot 'modelo\doc\project_methodology_manifest.json'
$methodologyTargetPath = Join-Path $resolvedProject 'doc\project_methodology_manifest.json'
$created = @()

if (-not (Test-Path -LiteralPath $methodologyTargetPath -PathType Leaf)) {
    $methodology = Get-Content -LiteralPath $methodologyTemplatePath -Raw -Encoding UTF8 | ConvertFrom-Json
    $methodology.project.name = $ProjectName
    $methodology.project.lifecycle = $Lifecycle
    Write-JsonUtf8 $methodologyTargetPath $methodology
    $created += $methodologyTargetPath
}

$contextTemplatePath = Join-Path $PSScriptRoot 'modelo\doc\project_context_manifest.json'
$contextTargetPath = Join-Path $resolvedProject 'doc\project_context_manifest.json'
if (-not (Test-Path -LiteralPath $contextTargetPath -PathType Leaf)) {
    Copy-Item -LiteralPath $contextTemplatePath -Destination $contextTargetPath
    $created += $contextTargetPath
}

$contextDocTemplates = @(
    '00-project-brief.md',
    '15-tdd.md',
    '16-ldd.md',
    '17-audio-design.md',
    '18-asset-register.json',
    '19-roadmap-risk-register.md',
    '20-release-marketing-legal.md',
    '21-review-consulting-context.md'
)
foreach ($docName in $contextDocTemplates) {
    $docTemplatePath = Join-Path (Join-Path $PSScriptRoot 'modelo\doc') $docName
    $docTargetPath = Join-Path (Join-Path $resolvedProject 'doc') $docName
    if (Test-Path -LiteralPath $docTargetPath -PathType Leaf) {
        continue
    }
    $content = Get-Content -LiteralPath $docTemplatePath -Raw -Encoding UTF8
    $content = $content.Replace('__PROJECT_NAME__', $ProjectName)
    [System.IO.File]::WriteAllText($docTargetPath, $content, [System.Text.Encoding]::UTF8)
    $created += $docTargetPath
}

$techniqueTemplatePath = Join-Path $PSScriptRoot 'modelo\doc\technique_usage_manifest.json'
$techniqueTargetPath = Join-Path $resolvedProject 'doc\technique_usage_manifest.json'
if (-not (Test-Path -LiteralPath $techniqueTargetPath -PathType Leaf)) {
    $technique = Get-Content -LiteralPath $techniqueTemplatePath -Raw -Encoding UTF8 | ConvertFrom-Json
    $technique.project.name = $ProjectName
    $kind = if ($projectManifest -and $projectManifest.PSObject.Properties['kind']) { [string]$projectManifest.kind } else { '' }
    $category = if ($projectManifest -and $projectManifest.PSObject.Properties['category']) { [string]$projectManifest.category } else { '' }
    $technique.project.lab_not_delivery = ($kind -match '(?i)(lab|techdemo|prototype)' -or $category -match '(?i)(lab|techdemo|prototype)')
    Write-JsonUtf8 $techniqueTargetPath $technique
    $created += $techniqueTargetPath
}

$hygieneTemplatePath = Join-Path $PSScriptRoot 'modelo\doc\project_hygiene_manifest.json'
$hygieneTargetPath = Join-Path $resolvedProject 'doc\project_hygiene_manifest.json'
if (-not (Test-Path -LiteralPath $hygieneTargetPath -PathType Leaf)) {
    Copy-Item -LiteralPath $hygieneTemplatePath -Destination $hygieneTargetPath
    $created += $hygieneTargetPath
}

$learningTemplateRoot = Join-Path $PSScriptRoot 'modelo\doc\agent_learning'
$learningTargetRoot = Join-Path $resolvedProject 'doc\agent_learning'
if (-not (Test-Path -LiteralPath $learningTargetRoot -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $learningTargetRoot | Out-Null
}
foreach ($learningTemplate in @(Get-ChildItem -LiteralPath $learningTemplateRoot -File)) {
    $learningTarget = Join-Path $learningTargetRoot $learningTemplate.Name
    if (Test-Path -LiteralPath $learningTarget -PathType Leaf) {
        continue
    }

    if ($learningTemplate.Name -eq 'learning_ledger.json') {
        $ledger = Get-Content -LiteralPath $learningTemplate.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        $ledger.project.name = $ProjectName
        Write-JsonUtf8 $learningTarget $ledger
    } else {
        $content = Get-Content -LiteralPath $learningTemplate.FullName -Raw -Encoding UTF8
        $content = $content.Replace('__PROJECT_NAME__', $ProjectName)
        [System.IO.File]::WriteAllText($learningTarget, $content, [System.Text.Encoding]::UTF8)
    }
    $created += $learningTarget
}

$aiMemoryScript = Join-Path $PSScriptRoot 'prepare_ai_memory_integration.ps1'
if (Test-Path -LiteralPath $aiMemoryScript -PathType Leaf) {
    $workspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
    $aiArgs = @(
        '-NoProfile',
        '-ExecutionPolicy', 'Bypass',
        '-File', $aiMemoryScript,
        '-RepoRoot', $workspaceRoot,
        '-ProjectRoot', $resolvedProject,
        '-Mode', 'Prepare',
        '-OutputFormat', 'Json'
    )
    $powerShellHost = Resolve-PowerShellHost
    $aiOut = (& $powerShellHost @aiArgs 2>&1 | Out-String)
    if ($LASTEXITCODE -eq 0) {
        try {
            $aiReport = $aiOut | ConvertFrom-Json
            if (@('created', 'updated') -contains [string]$aiReport.actions.project_marker_write_status) {
                $created += (Join-Path $resolvedProject '.ai-memory.toml')
            }
        } catch {
            Write-Warning "ai-memory report unreadable; continuing methodology adoption."
        }
    } else {
        Write-Warning "ai-memory consultive marker was not prepared; continuing methodology adoption."
    }
}

$scratchRoot = Join-Path $resolvedProject 'rascunho'
if (-not (Test-Path -LiteralPath $scratchRoot -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $scratchRoot | Out-Null
}
$scratchReadmeTemplate = Join-Path $PSScriptRoot 'modelo\rascunho\README.md'
$scratchReadmeTarget = Join-Path $scratchRoot 'README.md'
if (-not (Test-Path -LiteralPath $scratchReadmeTarget -PathType Leaf)) {
    Copy-Item -LiteralPath $scratchReadmeTemplate -Destination $scratchReadmeTarget
    $created += $scratchReadmeTarget
}

if ($created.Count -gt 0) {
    Write-Host ("[adopt_project_methodology] materialized={0}" -f ($created -join ','))
} else {
    Write-Host '[adopt_project_methodology] existing manifests preserved; no files changed.'
}
exit 0
