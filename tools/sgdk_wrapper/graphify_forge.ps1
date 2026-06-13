param(
    [Parameter(Mandatory)]
    [ValidateSet('build', 'update', 'query', 'report', 'status', 'mark-stale')]
    [string]$Action,

    [string]$RepoRoot = '',

    [string]$Question = '',

    [int]$Budget = 2000,

    [switch]$Force,

    [switch]$AllowStale
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-RepoRoot {
    param([string]$Provided)

    if ($Provided) {
        return (Resolve-Path -LiteralPath $Provided).Path
    }

    $wrapperRoot = $PSScriptRoot
    return (Resolve-Path -LiteralPath (Split-Path (Split-Path $wrapperRoot -Parent) -Parent)).Path
}

function Get-ForgeTrackedRoots {
    param([string]$Root)
    return @(
        (Join-Path $Root 'tools\sgdk_wrapper\.agent'),
        (Join-Path $Root 'doc\05_technical'),
        (Join-Path $Root 'doc\07_game_design'),
        (Join-Path $Root 'doc\06_AI_MEMORY_BANK.md')
    )
}

function Get-ForgeTrackedFiles {
    param([string]$Root)

    $roots = Get-ForgeTrackedRoots -Root $Root
    $files = New-Object System.Collections.Generic.List[System.IO.FileInfo]

    foreach ($p in $roots) {
        if (-not (Test-Path -LiteralPath $p)) { continue }
        if ((Get-Item -LiteralPath $p) -is [System.IO.DirectoryInfo]) {
            Get-ChildItem -LiteralPath $p -Recurse -File | Where-Object {
                $_.FullName -notmatch '\\__pycache__\\' -and
                $_.FullName -notmatch '\\\.pytest_cache\\' -and
                $_.FullName -notmatch '\\\.serena\\' -and
                $_.FullName -notmatch '\\\.superpowers\\' -and
                $_.Extension -ne '.pyc'
            } | ForEach-Object { $files.Add($_) }
        } else {
            $files.Add((Get-Item -LiteralPath $p))
        }
    }

    return $files
}

function New-ForgeFreshnessSnapshot {
    param([string]$Root)

    $trackedFiles = Get-ForgeTrackedFiles -Root $Root
    $entries = New-Object System.Collections.Generic.List[object]

    foreach ($f in $trackedFiles) {
        $abs = (Resolve-Path -LiteralPath $f.FullName).Path.Replace('\', '/')
        $entries.Add([pscustomobject]@{
            path = $abs
            length = [int64]$f.Length
            last_write_time_utc_ticks = [int64]$f.LastWriteTimeUtc.Ticks
        })
    }

    $entriesSorted = $entries | Sort-Object -Property path
    return [pscustomobject]@{
        repo_root = $Root.Replace('\', '/')
        created_at_utc = (Get-Date).ToUniversalTime().ToString('o')
        tracked_paths = @(
            'tools/sgdk_wrapper/.agent/**',
            'doc/05_technical/**',
            'doc/07_game_design/**',
            'doc/06_AI_MEMORY_BANK.md'
        )
        files = $entriesSorted
        forced_stale = $false
    }
}

function Read-JsonFile {
    param([string]$Path)
    return (Get-Content -LiteralPath $Path -Raw) | ConvertFrom-Json
}

function Write-JsonFile {
    param([string]$Path, [object]$Obj)
    $dir = Split-Path $Path -Parent
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $json = $Obj | ConvertTo-Json -Depth 50
    Set-Content -LiteralPath $Path -Value $json -Encoding UTF8
}

function Test-PathUnderRoot {
    param(
        [string]$Path,
        [string]$Root
    )

    $p = [System.IO.Path]::GetFullPath($Path)
    $r = [System.IO.Path]::GetFullPath($Root)

    if ($p -ieq $r) { return $true }

    $rWithSep = $r
    if (-not $rWithSep.EndsWith('\')) { $rWithSep += '\' }
    return $p.StartsWith($rWithSep, [System.StringComparison]::OrdinalIgnoreCase)
}

function Get-ForgeScopeViolationTokensFromText {
    param(
        [string]$Text
    )

    $tokens = New-Object System.Collections.Generic.List[string]
    if (-not $Text) { return $tokens }

    $norm = $Text.Replace('\', '/').ToLowerInvariant()
    $srcMatches = [regex]::Matches($norm, 'src=([^\s\]\)>,;]+)')
    foreach ($m in $srcMatches) {
        $v = [string]$m.Groups[1].Value
        if ($v) { $tokens.Add($v) }
    }

    return $tokens
}

function Get-ForgeScopeViolationsFromStrings {
    param(
        [string[]]$Strings
    )

    $violations = New-Object System.Collections.Generic.List[string]

    foreach ($s in $Strings) {
        if (-not $s) { continue }
        $norm = $s.Trim().Replace('\', '/').ToLowerInvariant()
        if (-not $norm) { continue }
        if ($norm -match '^[a-z][a-z0-9+\.-]*://') { continue }

        $srcTokens = Get-ForgeScopeViolationTokensFromText -Text $norm
        $candidates = @($norm) + $srcTokens

        foreach ($p in $candidates) {
            if (-not $p) { continue }
            $pn = [string]$p
            $pn = $pn.Trim().Replace('\', '/').ToLowerInvariant()
            if (-not $pn) { continue }
            if ($pn -match '^[a-z][a-z0-9+\.-]*://') { continue }

            if ($pn -match '(^|/)\.graphifyignore$') { continue }
            if ($pn -match '(^|/)\.gitignore$') { continue }
            if ($pn -match '(^|/)doc/06_ai_memory_bank\.md') { continue }
            if ($pn -match '(^|/)doc/05_technical(/|$)') { continue }
            if ($pn -match '(^|/)doc/07_game_design(/|$)') { continue }
            if ($pn -match '(^|/)tools/sgdk_wrapper/\.agent(/|$)') { continue }

            if ($pn -match '(^|/)tools/sgdk_wrapper/modelo(/|$)') { $violations.Add($pn); continue }
            if ($pn -match '(^|/)sgdk_projects(/|$)') { $violations.Add($pn); continue }
            if ($pn -match '(^|/)sdk(/|$)') { $violations.Add($pn); continue }
            if ($pn -match '(^|/)tools/emuladores(/|$)') { $violations.Add($pn); continue }
            if ($pn -match '(^|/)out(/|$)') { $violations.Add($pn); continue }
            if ($pn -match '(^|/)graphify-out(/|$)') { $violations.Add($pn); continue }
            if ($pn -match '(^|/)\.pytest_cache(/|$)') { $violations.Add($pn); continue }
            if ($pn -match '(^|/)\.serena(/|$)') { $violations.Add($pn); continue }
            if ($pn -match '(^|/)\.superpowers(/|$)') { $violations.Add($pn); continue }

            if ($pn -match '(^|/)doc(/|$)') { $violations.Add($pn); continue }
            if ($pn -match '(^|/)tools(/|$)') { $violations.Add($pn); continue }
        }
    }

    return ,($violations.ToArray())
}

function Get-ForgeGraphPathCandidates {
    param([object]$Obj)

    $out = New-Object System.Collections.Generic.List[string]
    $pathKeys = @{}
    foreach ($k in @('source_file', 'source_path', 'path', 'file', 'source', 'sourcefile', 'sourcelocation')) {
        $pathKeys[$k] = $true
    }

    function Walk {
        param(
            [string]$PropName,
            [object]$Value
        )

        if ($null -eq $Value) { return }

        if ($Value -is [string]) {
            if ($PropName -and $pathKeys.ContainsKey($PropName.ToLowerInvariant())) {
                $out.Add([string]$Value)
                foreach ($srcToken in (Get-ForgeScopeViolationTokensFromText -Text ([string]$Value))) {
                    $out.Add([string]$srcToken)
                }
            }
            return
        }

        if ($Value -is [System.Collections.IDictionary]) {
            foreach ($k in $Value.Keys) {
                $kn = ''
                if ($null -ne $k) { $kn = [string]$k }
                Walk -PropName $kn -Value $Value[$k]
            }
            return
        }

        if ($Value -is [System.Collections.IEnumerable] -and -not ($Value -is [string])) {
            foreach ($x in $Value) { Walk -PropName $PropName -Value $x }
            return
        }

        foreach ($p in $Value.PSObject.Properties) {
            Walk -PropName $p.Name -Value $p.Value
        }
    }

    Walk -PropName '' -Value $Obj
    return $out
}

function Test-ForgeGraphScope {
    param([string]$GraphJsonPath)

    if (-not (Test-Path -LiteralPath $GraphJsonPath)) {
        return [pscustomobject]@{ is_in_scope = $false; reason = 'graph_missing'; sample = @() }
    }

    $raw = Get-Content -LiteralPath $GraphJsonPath -Raw
    $obj = $raw | ConvertFrom-Json
    $paths = Get-ForgeGraphPathCandidates -Obj $obj

    $violations = Get-ForgeScopeViolationsFromStrings -Strings $paths
    if ($violations.Count -gt 0) {
        $sample = $violations | Select-Object -First 5
        return [pscustomobject]@{ is_in_scope = $false; reason = 'graph_scope_violation'; sample = $sample }
    }

    return [pscustomobject]@{ is_in_scope = $true; reason = 'ok'; sample = @() }
}

function Test-ForgeFreshness {
    param(
        [string]$Root,
        [string]$GraphJsonPath,
        [string]$FreshnessPath
    )

    if (-not (Test-Path -LiteralPath $GraphJsonPath)) {
        return [pscustomobject]@{ is_fresh = $false; reason = 'graph_missing' }
    }

    $scope = Test-ForgeGraphScope -GraphJsonPath $GraphJsonPath
    if (-not $scope.is_in_scope) {
        return [pscustomobject]@{ is_fresh = $false; reason = $scope.reason; scope_sample = $scope.sample }
    }
    if (-not (Test-Path -LiteralPath $FreshnessPath)) {
        return [pscustomobject]@{ is_fresh = $false; reason = 'freshness_missing' }
    }

    $prev = Read-JsonFile -Path $FreshnessPath
    $forcedStaleProp = $prev.PSObject.Properties['forced_stale']
    if ($null -ne $forcedStaleProp -and [bool]$forcedStaleProp.Value) {
        return [pscustomobject]@{ is_fresh = $false; reason = 'forced_stale' }
    }

    $curr = New-ForgeFreshnessSnapshot -Root $Root

    $prevIndex = @{}
    foreach ($f in $prev.files) { $prevIndex[$f.path] = $f }

    $changed = 0
    foreach ($f in $curr.files) {
        $p = $f.path
        if (-not $prevIndex.ContainsKey($p)) { $changed++; continue }
        $pf = $prevIndex[$p]
        if ([int64]$pf.length -ne [int64]$f.length) { $changed++; continue }
        $prevTicks = $null
        if ($null -ne $pf.last_write_time_utc_ticks) {
            $prevTicks = [int64]$pf.last_write_time_utc_ticks
        } elseif ($null -ne $pf.last_write_time_utc) {
            $prevTicks = [int64]([datetime]$pf.last_write_time_utc).ToUniversalTime().Ticks
        }

        if ($null -eq $prevTicks -or [int64]$prevTicks -ne [int64]$f.last_write_time_utc_ticks) { $changed++; continue }
    }

    if ($changed -gt 0 -or $prev.files.Count -ne $curr.files.Count) {
        return [pscustomobject]@{ is_fresh = $false; reason = 'tracked_paths_changed' }
    }

    return [pscustomobject]@{ is_fresh = $true; reason = 'ok' }
}

function Require-GraphifyInstalled {
    $cmd = Get-Command graphify -ErrorAction SilentlyContinue
    if ($null -eq $cmd) {
        Write-Host 'graphify nao encontrado no PATH. Instale com: uv tool install graphifyy'
        exit 3
    }
}

$resolvedRepoRoot = Resolve-RepoRoot -Provided $RepoRoot
$graphifyOutDir = Join-Path $resolvedRepoRoot 'graphify-out'
$graphJsonPath = Join-Path $graphifyOutDir 'graph.json'
$freshnessPath = Join-Path $graphifyOutDir 'FORGE_FRESHNESS.json'
$forgeReportPath = Join-Path $graphifyOutDir 'FORGE_GRAPHIFY_REPORT.md'

if ($Action -in @('build', 'update', 'query', 'report', 'status', 'mark-stale')) {
    Require-GraphifyInstalled
}

if ($Action -eq 'build') {
    $canonicalWorkspaceRoot = Resolve-RepoRoot -Provided ''
    if (-not (Test-PathUnderRoot -Path $graphifyOutDir -Root $canonicalWorkspaceRoot)) {
        Write-Host 'Bloqueado: tentativa de remover graphify-out fora do workspace canonico.'
        Write-Host "workspace_root=$canonicalWorkspaceRoot"
        Write-Host "target=$graphifyOutDir"
        exit 6
    }

    if (Test-Path -LiteralPath $graphifyOutDir) {
        Remove-Item -LiteralPath $graphifyOutDir -Recurse -Force
    }

    $args = @('update', $resolvedRepoRoot, '--force')
    $captured = @()
    & graphify @args 2>&1 | Tee-Object -Variable captured | Out-Host
    $updateOut = ($captured | Out-String)

    $scope = Test-ForgeGraphScope -GraphJsonPath $graphJsonPath
    if (-not $scope.is_in_scope) {
        Write-Host "graph_status=stale reason=$($scope.reason)"
        $scopeSample = @($scope.sample)
        if ($scopeSample.Count -gt 0) { Write-Host ("scope_sample=" + ($scopeSample -join ', ')) }
        Write-Host 'Bloqueado: grafo contaminado por fontes fora do escopo.'
        exit 6
    }

    $snapshot = New-ForgeFreshnessSnapshot -Root $resolvedRepoRoot
    Write-JsonFile -Path $freshnessPath -Obj $snapshot
    exit 0
}

if ($Action -eq 'update') {
    $args = @('update', $resolvedRepoRoot)
    if ($Force) { $args += '--force' }
    $captured = @()
    & graphify @args 2>&1 | Tee-Object -Variable captured | Out-Host
    $updateOut = ($captured | Out-String)

    $scope = Test-ForgeGraphScope -GraphJsonPath $graphJsonPath
    if (-not $scope.is_in_scope) {
        Write-Host "graph_status=stale reason=$($scope.reason)"
        $scopeSample = @($scope.sample)
        if ($scopeSample.Count -gt 0) { Write-Host ("scope_sample=" + ($scopeSample -join ', ')) }
        Write-Host 'Bloqueado: grafo contaminado por fontes fora do escopo.'
        if ($updateOut -match 'outputs left untouched') {
            Write-Host 'Graphify deixou outputs intactos; rode clean build.'
            Write-Host "Rode: pwsh -File tools/sgdk_wrapper/graphify_forge.ps1 -Action build -RepoRoot `"$resolvedRepoRoot`" -Force"
        } else {
            Write-Host "Rode: pwsh -File tools/sgdk_wrapper/graphify_forge.ps1 -Action build -RepoRoot `"$resolvedRepoRoot`""
        }
        exit 6
    }

    $snapshot = New-ForgeFreshnessSnapshot -Root $resolvedRepoRoot
    Write-JsonFile -Path $freshnessPath -Obj $snapshot
    exit 0
}

if ($Action -eq 'mark-stale') {
    if (-not (Test-Path -LiteralPath $freshnessPath)) {
        $snapshot = New-ForgeFreshnessSnapshot -Root $resolvedRepoRoot
        $snapshot.forced_stale = $true
        Write-JsonFile -Path $freshnessPath -Obj $snapshot
        exit 0
    }

    $prev = Read-JsonFile -Path $freshnessPath
    $prev.forced_stale = $true
    Write-JsonFile -Path $freshnessPath -Obj $prev
    exit 0
}

$fresh = Test-ForgeFreshness -Root $resolvedRepoRoot -GraphJsonPath $graphJsonPath -FreshnessPath $freshnessPath

if ($Action -eq 'status') {
    $status = if ($fresh.is_fresh) { 'fresh' } else { 'stale' }
    Write-Host "graph_status=$status reason=$($fresh.reason)"
    $freshScopeSample = @()
    $scopeProp = $fresh.PSObject.Properties['scope_sample']
    if ($null -ne $scopeProp) { $freshScopeSample = @($scopeProp.Value) }
    if ($freshScopeSample.Count -gt 0) {
        Write-Host ("scope_sample=" + ($freshScopeSample -join ', '))
    }
    exit 0
}

if ($Action -eq 'query') {
    if (-not $Question) {
        Write-Host 'Question obrigatoria para action=query'
        exit 4
    }

    if (-not $fresh.is_fresh -and -not $AllowStale) {
        Write-Host "graph_status=stale reason=$($fresh.reason)"
        if ($fresh.reason -eq 'graph_scope_violation') {
            Write-Host 'Bloqueado: grafo contaminado por fontes fora do escopo. Rode clean build.'
            Write-Host "Rode: pwsh -File tools/sgdk_wrapper/graphify_forge.ps1 -Action build -RepoRoot `"$resolvedRepoRoot`" -Force"
        } else {
            Write-Host 'Bloqueado: grafo stale nao pode ser usado como autoridade.'
            Write-Host "Rode: pwsh -File tools/sgdk_wrapper/graphify_forge.ps1 -Action update -RepoRoot `"$resolvedRepoRoot`""
        }
        exit 2
    }

    $queryOut = (& graphify query $Question --budget $Budget --graph $graphJsonPath 2>&1 | Out-String)
    $qViol = Get-ForgeScopeViolationsFromStrings -Strings @($queryOut)
    if ($qViol.Count -gt 0) {
        $sample = ($qViol | Select-Object -First 1)
        Write-Host "Bloqueado: query retornou fonte fora de escopo: $sample Rode clean build."
        exit 6
    }

    $queryOut | Out-Host
    Write-Host ''
    Write-Host 'Regra: use o grafo apenas para localizar. Antes de decidir/editar, abra os arquivos canonicos citados.'
    exit 0
}

if ($Action -eq 'report') {
    $status = if ($fresh.is_fresh) { 'fresh' } else { 'stale' }
    $nowUtc = (Get-Date).ToUniversalTime().ToString('o')

    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add('# FORGE - Graphify Report')
    $lines.Add('')
    $lines.Add("generated_at_utc: $nowUtc")
    $lines.Add("graph_status: $status")
    $lines.Add("graph_reason: $($fresh.reason)")
    $lines.Add('')
    $lines.Add('Escopo indexado (consultivo):')
    $lines.Add('- tools/sgdk_wrapper/.agent/')
    $lines.Add('- doc/05_technical/')
    $lines.Add('- doc/07_game_design/')
    $lines.Add('- doc/06_AI_MEMORY_BANK.md')
    $lines.Add('')
    $lines.Add('Artefatos gerados (nao canonicos):')
    $lines.Add('- graphify-out/graph.json')
    if (Test-Path -LiteralPath (Join-Path $graphifyOutDir 'graph.html')) {
        $lines.Add('- graphify-out/graph.html')
    }
    $lines.Add('- graphify-out/GRAPH_REPORT.md')
    $lines.Add('- graphify-out/FORGE_FRESHNESS.json')
    $lines.Add('')
    $lines.Add('Comandos:')
    $lines.Add("- update: pwsh -File tools/sgdk_wrapper/graphify_forge.ps1 -Action update -RepoRoot `"$resolvedRepoRoot`"")
    $lines.Add("- status: pwsh -File tools/sgdk_wrapper/graphify_forge.ps1 -Action status -RepoRoot `"$resolvedRepoRoot`"")
    $lines.Add("- query:  pwsh -File tools/sgdk_wrapper/graphify_forge.ps1 -Action query -RepoRoot `"$resolvedRepoRoot`" -Question `"...`"")
    $lines.Add('')
    $lines.Add('Regra de uso:')
    $lines.Add('1. Use Graphify para localizar arquivos e relacionamentos.')
    $lines.Add('2. Abra a fonte canonica antes de qualquer decisao ou patch.')
    $lines.Add('3. Se graph_status=stale, rode update e repita a consulta.')

    if (-not (Test-Path -LiteralPath $graphifyOutDir)) { New-Item -ItemType Directory -Force -Path $graphifyOutDir | Out-Null }
    Set-Content -LiteralPath $forgeReportPath -Value ($lines -join "`n") -Encoding UTF8
    Write-Host "wrote=$forgeReportPath"
    exit 0
}

Write-Host "acao desconhecida: $Action"
exit 5
