Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$repoRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$scriptPath = Join-Path $wrapperRoot 'prepare_ai_memory_integration.ps1'
$fixtureRoot = Join-Path $repoRoot 'out\ci\ai_memory_integration_fixture'
$projectRoot = Join-Path $fixtureRoot 'SGDK_projects\Example Project [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]'

$passed = 0
$failed = 0
$total = 0

function Assert-True {
    param([string]$Name, [bool]$Condition)
    $script:total++
    if ($Condition) {
        $script:passed++
        Write-Host "  [PASS] $Name"
    } else {
        $script:failed++
        Write-Host "  [FAIL] $Name"
    }
}

function Assert-ExitCode {
    param([string]$Name, [int]$ExitCode, [int]$Expected)
    $script:total++
    if ($ExitCode -eq $Expected) {
        $script:passed++
        Write-Host "  [PASS] $Name"
    } else {
        $script:failed++
        Write-Host "  [FAIL] $Name (got=$ExitCode expected=$Expected)"
    }
}

function Test-PowerShellSyntax {
    param([string]$Path)
    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$tokens, [ref]$errors) | Out-Null
    return ($errors.Count -eq 0)
}

function Get-TreeDigest {
    param([string]$Root)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = New-Object System.Collections.Generic.List[byte]
        $rootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd('\') + '\'
        foreach ($file in @(Get-ChildItem -LiteralPath $Root -Recurse -File | Sort-Object FullName)) {
            $fileFull = [System.IO.Path]::GetFullPath($file.FullName)
            $rel = $fileFull.Substring($rootFull.Length).Replace('\', '/')
            $pathBytes = [System.Text.Encoding]::UTF8.GetBytes($rel)
            $contentBytes = [System.IO.File]::ReadAllBytes($file.FullName)
            $bytes.AddRange($pathBytes)
            $bytes.Add(0)
            $bytes.AddRange($contentBytes)
            $bytes.Add(0)
        }
        return ([BitConverter]::ToString($sha.ComputeHash($bytes.ToArray())) -replace '-', '').ToLowerInvariant()
    } finally {
        $sha.Dispose()
    }
}

function Invoke-AiMemoryPrepare {
    param([string[]]$ArgumentList)
    $out = (& powershell -NoProfile -ExecutionPolicy Bypass -File $scriptPath @ArgumentList 2>&1 | Out-String)
    return [pscustomobject]@{
        ExitCode = $LASTEXITCODE
        Output = $out
    }
}

Write-Host ''
Write-Host '=== AI Memory Controlled Integration ==='
Write-Host ''

Assert-True 'prepare_ai_memory_integration.ps1 existe' (Test-Path -LiteralPath $scriptPath -PathType Leaf)
if (Test-Path -LiteralPath $scriptPath -PathType Leaf) {
    Assert-True 'prepare_ai_memory_integration.ps1 sintaxe ok' (Test-PowerShellSyntax -Path $scriptPath)
}

if (Test-Path -LiteralPath $fixtureRoot -PathType Container) {
    $resolvedFixture = (Resolve-Path -LiteralPath $fixtureRoot).Path
    $resolvedCiRoot = (Resolve-Path -LiteralPath (Join-Path $repoRoot 'out\ci')).Path
    if ($resolvedFixture.StartsWith($resolvedCiRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        Remove-Item -LiteralPath $resolvedFixture -Recurse -Force
    }
}
New-Item -ItemType Directory -Force -Path $projectRoot | Out-Null

if (Test-Path -LiteralPath $scriptPath -PathType Leaf) {
    $prepare = Invoke-AiMemoryPrepare -ArgumentList @(
        '-RepoRoot', $fixtureRoot,
        '-ProjectRoot', $projectRoot,
        '-Mode', 'Prepare',
        '-OutputFormat', 'Json',
        '-WorkspaceId', 'sgdk_forge_test'
    )
    Assert-ExitCode 'Prepare sai com sucesso' $prepare.ExitCode 0

    $report = $prepare.Output | ConvertFrom-Json
    Assert-True 'report declara camada consultiva' ([string]$report.policy.authority -eq 'consultive_only')
    Assert-True 'report proibe mutacao canonica automatica' (-not [bool]$report.policy.canonical_auto_mutation)
    Assert-True 'report nao instalou hooks globais' (-not [bool]$report.actions.install_hooks_apply_performed)
    Assert-True 'report nao instalou MCP global' (-not [bool]$report.actions.install_mcp_apply_performed)

    $rootMarker = Join-Path $fixtureRoot '.ai-memory.toml'
    $projectMarker = Join-Path $projectRoot '.ai-memory.toml'
    $policyDoc = Join-Path $fixtureRoot 'doc\AI_MEMORY_POLICY.md'
    $writtenReport = Join-Path $fixtureRoot 'out\logs\ai_memory_integration_report.json'

    Assert-True 'marcador raiz criado' (Test-Path -LiteralPath $rootMarker -PathType Leaf)
    Assert-True 'marcador de projeto criado' (Test-Path -LiteralPath $projectMarker -PathType Leaf)
    Assert-True 'politica canonica criada no fixture' (Test-Path -LiteralPath $policyDoc -PathType Leaf)
    Assert-True 'report runtime criado em out/logs' (Test-Path -LiteralPath $writtenReport -PathType Leaf)

    $rootMarkerText = Get-Content -LiteralPath $rootMarker -Raw
    $projectMarkerText = Get-Content -LiteralPath $projectMarker -Raw
    Assert-True 'marcador raiz usa workspace controlado' ($rootMarkerText -match 'workspace = "sgdk_forge_test"')
    Assert-True 'marcador raiz usa projeto workspace' ($rootMarkerText -match 'project = "workspace"')
    Assert-True 'marcador de projeto usa slug portavel' ($projectMarkerText -match 'project = "example_project_ver.001_sgdk_211_gen_lab_techdemo"')

    $beforeAudit = Get-TreeDigest -Root $fixtureRoot
    $audit = Invoke-AiMemoryPrepare -ArgumentList @(
        '-RepoRoot', $fixtureRoot,
        '-ProjectRoot', $projectRoot,
        '-Mode', 'Audit',
        '-OutputFormat', 'Json',
        '-WorkspaceId', 'sgdk_forge_test'
    )
    $afterAudit = Get-TreeDigest -Root $fixtureRoot
    Assert-ExitCode 'Audit sai com sucesso' $audit.ExitCode 0
    Assert-True 'Audit nao altera arquivos' ($beforeAudit -eq $afterAudit)

    $auditReport = $audit.Output | ConvertFrom-Json
    Assert-True 'Audit reconhece marcadores existentes' (
        [string]$auditReport.root_marker.status -eq 'present' -and
        [string]$auditReport.project_marker.status -eq 'present'
    )
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
