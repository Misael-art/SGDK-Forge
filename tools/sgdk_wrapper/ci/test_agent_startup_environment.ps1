Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$repoRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent
$prepareScript = Join-Path $wrapperRoot 'prepare_agent_environment.ps1'
$assertScript = Join-Path $wrapperRoot 'assert_agent_environment.ps1'
$aiMemoryScript = Join-Path $wrapperRoot 'prepare_ai_memory_integration.ps1'
$menuScript = Join-Path $wrapperRoot 'show_agent_menu.ps1'
$reportPath = Join-Path $repoRoot 'graphify-out\AGENT_ENVIRONMENT_REPORT.json'

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

Write-Host ''
Write-Host '=== Agent Startup Environment ==='
Write-Host ''

Assert-True 'prepare_agent_environment.ps1 existe' (Test-Path -LiteralPath $prepareScript -PathType Leaf)
Assert-True 'assert_agent_environment.ps1 existe' (Test-Path -LiteralPath $assertScript -PathType Leaf)
Assert-True 'prepare_ai_memory_integration.ps1 existe' (Test-Path -LiteralPath $aiMemoryScript -PathType Leaf)
Assert-True 'prepare_agent_environment.ps1 sintaxe ok' (Test-PowerShellSyntax -Path $prepareScript)
Assert-True 'assert_agent_environment.ps1 sintaxe ok' (Test-PowerShellSyntax -Path $assertScript)
Assert-True 'prepare_ai_memory_integration.ps1 sintaxe ok' (Test-PowerShellSyntax -Path $aiMemoryScript)

$assertOut = (& powershell -NoProfile -ExecutionPolicy Bypass -File $assertScript -RepoRoot $repoRoot -GraphifyTimeoutSeconds 15 2>&1 | Out-String)
$assertExit = $LASTEXITCODE
Write-Host $assertOut.TrimEnd()
Assert-True 'AGENT_ENVIRONMENT_REPORT.json existe' (Test-Path -LiteralPath $reportPath -PathType Leaf)

$report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
$graphifyControlledBlocker = (
    $assertExit -ne 0 -and
    $assertOut -match 'graphify_start_failed|graphify_timeout|graph_not_fresh|prepare_failed' -and
    [string]$report.graphify.status -ne 'fresh'
)

if ($graphifyControlledBlocker) {
    Assert-True 'assert reporta blocker Graphify controlado' $true
    Assert-True 'report.ready=false por Graphify externo' (-not [bool]$report.ready)
} else {
    Assert-ExitCode 'assert_agent_environment prepara ambiente' $assertExit 0
    Assert-True 'assert reporta ready' ($assertOut -match 'agent_environment_status=ready')
    Assert-True 'report.ready=true' ([bool]$report.ready)
}
Assert-True 'report valida bridge .agents' ([bool]$report.checks.agents_skills_bridge)
Assert-True 'report valida bridge .trae' ([bool]$report.checks.trae_skills_bridge)
Assert-True 'report valida pwsh' ([bool]$report.checks.pwsh)
Assert-True 'report valida uv' ([bool]$report.checks.uv)
Assert-True 'report valida graphify' ([bool]$report.checks.graphify)
if ($graphifyControlledBlocker) {
    Assert-True 'report graphify degradado controlado' ([string]$report.graphify.status -ne 'fresh')
} else {
    Assert-True 'report graphify fresh' ([string]$report.graphify.status -eq 'fresh')
}
Assert-True 'report graphify timeout configurado' ([int]$report.graphify.timeout_seconds -eq 15)
Assert-True 'report contem ai_memory' ($null -ne $report.ai_memory)
Assert-True 'report ai_memory preparado' ([string]$report.ai_memory.status -eq 'prepared')
Assert-True 'report ai_memory consultivo' ([string]$report.ai_memory.policy -eq 'consultive_optional_layer')
Assert-True 'report ai_memory nao e gate de closeout' (-not [bool]$report.ai_memory.closeout_gate)

$entryFiles = @(
    'AGENTS.md',
    'CLAUDE.md',
    '.cursor/rules/session-bootstrap.mdc',
    '.cursor/rules/agent-startup-environment.mdc',
    '.serena/project.yml',
    '.agents/README.md',
    '.trae/README.md',
    '.superpowers/README.md',
    '.claude/README.md',
    'doc/GRAPHIFY_OBSIDIAN_POLICY.md',
    'tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md',
    'tools/sgdk_wrapper/.agent/workflows/agent-startup-environment.md'
)

foreach ($rel in $entryFiles) {
    $p = Join-Path $repoRoot $rel
    $txt = Get-Content -LiteralPath $p -Raw
    Assert-True "$rel menciona assert_agent_environment" ($txt -match 'assert_agent_environment\.ps1')
}

$menuText = Get-Content -LiteralPath $menuScript -Raw
Assert-True 'show_agent_menu chama guard automaticamente' ($menuText -match 'assert_agent_environment\.ps1')
Assert-True 'show_agent_menu tem opt-out explicito' ($menuText -match 'SGDK_SKIP_AGENT_ENVIRONMENT_GUARD')

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
