Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$wrapperRoot = Split-Path $PSScriptRoot -Parent
$repoRoot = Split-Path (Split-Path $wrapperRoot -Parent) -Parent

$graphifyForge = Join-Path $wrapperRoot 'graphify_forge.ps1'
$graphifyIgnore = Join-Path $repoRoot '.graphifyignore'

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

function Invoke-ForgeGraphify {
    param(
        [string]$Action,
        [string]$RepoRoot,
        [string]$Question = ''
    )

    $args = @(
        '-NoProfile',
        '-ExecutionPolicy', 'Bypass',
        '-File', $graphifyForge,
        '-Action', $Action,
        '-RepoRoot', $RepoRoot
    )

    if ($Question) {
        $args += @('-Question', $Question)
    }

    $output = (& pwsh @args 2>&1 | Out-String)
    $exitCode = $LASTEXITCODE

    return [pscustomobject]@{
        exit_code = $exitCode
        output = $output
    }
}

function Write-TextFile {
    param([string]$Path, [string]$Text)
    $parent = Split-Path $Path -Parent
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    [System.IO.File]::WriteAllText($Path, $Text, [System.Text.Encoding]::UTF8)
}

function Write-JsonFile {
    param([string]$Path, $Value)
    $parent = Split-Path $Path -Parent
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    [System.IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 20), [System.Text.Encoding]::UTF8)
}

function New-FreshnessSnapshot {
    param([string]$Root)
    $tracked = @(
        'tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md',
        'doc/05_technical/sample.md',
        'doc/07_game_design/sample.md',
        'doc/06_AI_MEMORY_BANK.md'
    )
    $entries = @()
    foreach ($relative in $tracked) {
        $path = Join-Path $Root $relative
        $item = Get-Item -LiteralPath $path
        $entries += [ordered]@{
            path = ([System.IO.Path]::GetFullPath($item.FullName)).Replace('\', '/')
            length = [int64]$item.Length
            last_write_time_utc_ticks = [int64]$item.LastWriteTimeUtc.Ticks
        }
    }
    return [ordered]@{
        repo_root = ([System.IO.Path]::GetFullPath($Root)).Replace('\', '/')
        created_at_utc = (Get-Date).ToUniversalTime().ToString('o')
        tracked_paths = @(
            'tools/sgdk_wrapper/.agent/**',
            'doc/05_technical/**',
            'doc/07_game_design/**',
            'doc/06_AI_MEMORY_BANK.md'
        )
        files = @($entries | Sort-Object -Property path)
    }
}

Write-Host ''
Write-Host '=== Graphify Integration ==='
Write-Host ''

Assert-True 'pwsh (PowerShell 7+) em uso' ($PSVersionTable.PSEdition -eq 'Core' -and $PSVersionTable.PSVersion.Major -ge 7)
Assert-True 'wrapper graphify_forge.ps1 existe' (Test-Path -LiteralPath $graphifyForge)
Assert-True '.graphifyignore existe' (Test-Path -LiteralPath $graphifyIgnore)

$testRoot = Join-Path $repoRoot 'out\graphify_test [brackets]'
$fixtureRoot = Join-Path $testRoot 'workspace [scope]'
$graphOut = Join-Path $fixtureRoot 'graphify-out'
$graphJson = Join-Path $graphOut 'graph.json'
$freshnessJson = Join-Path $graphOut 'FORGE_FRESHNESS.json'

try {
    if (Test-Path -LiteralPath $testRoot) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }

    New-Item -ItemType Directory -Force -Path $graphOut | Out-Null
    Copy-Item -LiteralPath $graphifyIgnore -Destination (Join-Path $fixtureRoot '.graphifyignore')
    Write-TextFile (Join-Path $fixtureRoot 'tools\sgdk_wrapper\.agent\rules\SGDK_GLOBAL.md') '# global rules'
    Write-TextFile (Join-Path $fixtureRoot 'doc\05_technical\sample.md') '# technical sample'
    Write-TextFile (Join-Path $fixtureRoot 'doc\07_game_design\sample.md') '# game design sample'
    Write-TextFile (Join-Path $fixtureRoot 'doc\06_AI_MEMORY_BANK.md') '# memory'

    Write-JsonFile $graphJson ([ordered]@{
        nodes = @(
            [ordered]@{ source_file = 'tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md' },
            [ordered]@{ source_file = 'doc/05_technical/sample.md' },
            [ordered]@{ source_file = 'doc/07_game_design/sample.md' },
            [ordered]@{ source_file = 'doc/06_AI_MEMORY_BANK.md' }
        )
        edges = @()
    })
    Write-JsonFile $freshnessJson (New-FreshnessSnapshot -Root $fixtureRoot)

    $statusFresh = Invoke-ForgeGraphify -Action 'status' -RepoRoot $fixtureRoot
    Assert-ExitCode 'status retorna 0 com fixture fresh' $statusFresh.exit_code 0
    Assert-True 'status indica fresh' ($statusFresh.output -match 'graph_status=fresh')

    Start-Sleep -Milliseconds 20
    Write-TextFile (Join-Path $fixtureRoot 'doc\06_AI_MEMORY_BANK.md') '# memory changed'

    $statusStale = Invoke-ForgeGraphify -Action 'status' -RepoRoot $fixtureRoot
    Assert-ExitCode 'status stale ainda retorna 0' $statusStale.exit_code 0
    Assert-True 'status stale detecta tracked_paths_changed' ($statusStale.output -match 'tracked_paths_changed')

    $queryStale = Invoke-ForgeGraphify -Action 'query' -RepoRoot $fixtureRoot -Question 'Qual e o papel do wrapper?'
    Assert-True 'query bloqueia grafo stale antes de chamar graphify query' ($queryStale.exit_code -ne 0)
    Assert-True 'query stale informa bloqueio' ($queryStale.output -match 'Bloqueado: grafo stale nao pode ser usado como autoridade')

    Write-JsonFile $freshnessJson (New-FreshnessSnapshot -Root $fixtureRoot)
    Write-JsonFile $graphJson ([ordered]@{
        nodes = @(
            [ordered]@{ source_file = 'tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md' },
            [ordered]@{ source_file = 'tools/sgdk_wrapper/modelo/.agent/ARCHITECTURE.md' }
        )
        edges = @()
    })

    $statusContam = Invoke-ForgeGraphify -Action 'status' -RepoRoot $fixtureRoot
    Assert-ExitCode 'status retorna 0 mesmo contaminado' $statusContam.exit_code 0
    Assert-True 'grafo contaminado nao fica fresh' ($statusContam.output -notmatch 'graph_status=fresh')
    Assert-True 'status aponta graph_scope_violation' ($statusContam.output -match 'graph_scope_violation')

    $queryContam = Invoke-ForgeGraphify -Action 'query' -RepoRoot $fixtureRoot -Question 'Onde fica a hierarquia?'
    Assert-True 'query bloqueia grafo contaminado' ($queryContam.exit_code -ne 0)
    Assert-True 'query contaminada pede clean build' ($queryContam.output -match 'Rode clean build')
}
finally {
    if (Test-Path -LiteralPath $testRoot) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }
}

Write-Host ''
Write-Host "=== Results: $passed/$total passed, $failed failed ==="
if ($failed -gt 0) { exit 1 }
exit 0
