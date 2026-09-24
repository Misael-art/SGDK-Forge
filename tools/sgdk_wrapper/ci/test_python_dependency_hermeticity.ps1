<#
.SYNOPSIS
    Prova que as dependencias Python dos gates vem do cache local do workspace,
    na versao do lock canonico, sem rede.

.DESCRIPTION
    Os validadores do framework importam `jsonschema` e `Pillow`. Sem hermetismo
    existem tres falsos verdes distintos, e todos ja aconteceram nesta classe de
    problema:

      1. o import resolve para o site-packages GLOBAL do sistema. O gate passa na
         maquina do desenvolvedor e falha em qualquer outra, ou pior: passa nas
         duas com versoes diferentes e ninguem percebe que o resultado nao e
         reproduzivel.
      2. a versao instalada nao e a do lock. O schema aceito por 4.25.1 pode ser
         rejeitado por outra minor, entao o veredito do gate depende do host.
      3. a dependencia esta ausente e o gate reporta "skip". Um gate que nao
         rodou nao pode contar como gate que passou -- e esse skip que transforma
         cobertura ausente em cobertura aparente.

    Este gate exige que as tres condicoes falhem RUIDOSAMENTE. Ele nao baixa
    nada: se o cache nao estiver pronto, isso e blocker, e a instrucao e rodar
    `ensure_linux_python_deps.sh` fora da janela dos gates.

    O lock e a UNICA autoridade de versao. O teste nunca escreve uma versao
    esperada literal; ele le o lock, exatamente como o codigo sob teste.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "../lib/host_executors_bootstrap.ps1")

$workspaceRoot = Get-WorkspaceRootFromModule
$failures = New-Object System.Collections.Generic.List[string]
$checks = 0

function Assert-True {
    param([string]$Label, [bool]$Condition, [string]$Detail = "")
    $script:checks++
    if ($Condition) {
        Write-Host "PASS $Label"
        return
    }
    if ([string]::IsNullOrWhiteSpace($Detail)) {
        $script:failures.Add($Label)
    } else {
        $script:failures.Add("${Label}: $Detail")
    }
    Write-Host "FAIL $Label $Detail"
}

# ---------------------------------------------------------------------------
# 1. Lock canonico unico
# ---------------------------------------------------------------------------

$lockPath = Get-PythonLockPath -WorkspaceRoot $workspaceRoot
Assert-True "lock canonico existe" (Test-Path -LiteralPath $lockPath -PathType Leaf) "path='$lockPath'"

# Um segundo lock e o inicio da divergencia: os gates leriam um e o provisionador
# o outro. Falhar aqui e mais barato que descobrir por hash divergente depois.
$rivalLocks = @(
    Get-ChildItem -LiteralPath (Split-Path $lockPath -Parent) -Filter "*requirements*.lock" -File |
        Where-Object { $_.FullName -ne (Resolve-Path -LiteralPath $lockPath).Path }
)
Assert-True "nenhum lock paralelo" ($rivalLocks.Count -eq 0) "rivais=$(($rivalLocks | ForEach-Object { $_.Name }) -join ',')"

$locked = Get-LockedPythonVersions -WorkspaceRoot $workspaceRoot
Assert-True "lock declara versoes fixadas" ($locked.Count -gt 0) "count=$($locked.Count)"

# --require-hashes so tem valor se TODA entrada tiver hash. Uma entrada sem hash
# aceitaria qualquer artefato com aquele nome/versao.
$lockText = Get-Content -LiteralPath $lockPath -Raw
$pinCount = ([regex]::Matches($lockText, '(?m)^[A-Za-z0-9_.\-]+==')).Count
$hashCount = ([regex]::Matches($lockText, '--hash=sha256:')).Count
Assert-True "toda entrada fixada tem hash sha256" ($hashCount -ge $pinCount) "pins=$pinCount hashes=$hashCount"

# ---------------------------------------------------------------------------
# 2. Provisionador canonico presente e sem versao duplicada
# ---------------------------------------------------------------------------

$ensureScript = Join-Path (Join-Path (Join-Path $workspaceRoot 'tools') 'sgdk_wrapper') 'ensure_linux_python_deps.sh'
Assert-True "provisionador existe" (Test-Path -LiteralPath $ensureScript -PathType Leaf) "path='$ensureScript'"

if (Test-Path -LiteralPath $ensureScript -PathType Leaf) {
    # O provisionador deve DERIVAR versoes do lock. Se ele repetir um numero de
    # versao, editar o lock deixa as duas fontes em desacordo silencioso.
    $ensureText = Get-Content -LiteralPath $ensureScript -Raw
    $hardcoded = @(
        [regex]::Matches($ensureText, '(?<![\d.])\d+\.\d+\.\d+(?![\d.])') |
            ForEach-Object { $_.Value } |
            Where-Object { $locked.Values -contains $_ } |
            Select-Object -Unique
    )
    Assert-True "provisionador nao duplica versao do lock" ($hardcoded.Count -eq 0) "duplicadas=$($hardcoded -join ',')"
    Assert-True "provisionador usa --require-hashes" ($ensureText -match '--require-hashes') ""
    Assert-True "provisionador instala com --no-index" ($ensureText -match '--no-index') ""
}

# ---------------------------------------------------------------------------
# 3. Estado real: cache pronto, versao do lock, procedencia local
# ---------------------------------------------------------------------------

$cachePath = Get-OfflinePythonPath -WorkspaceRoot $workspaceRoot
$cacheReady = Test-Path -LiteralPath $cachePath -PathType Container

if (-not $cacheReady) {
    # Blocker explicito, jamais skip.
    $failures.Add("python_cache_missing: '$cachePath' ausente. Rode tools/sgdk_wrapper/ensure_linux_python_deps.sh antes dos gates.")
    Write-Host "FAIL cache local presente (BLOCKER, nao skip)"
    Write-Host ""
    Write-Host "python dependency hermeticity: $checks verificacoes, $($failures.Count) falha(s)"
    foreach ($failure in $failures) { Write-Host "- $failure" }
    exit 1
}
Assert-True "cache local presente" $true

$resolved = Assert-PythonDependencies -WorkspaceRoot $workspaceRoot
foreach ($importName in @('jsonschema', 'PIL')) {
    $entry = $resolved.modules.$importName
    Assert-True "$importName importa" ($null -ne $entry) ""
    if ($null -ne $entry) {
        $want = $locked[([string]$entry.distribution).ToLowerInvariant()]
        Assert-True "$importName na versao do lock" ([string]$entry.version -eq [string]$want) "lock=$want instalado=$($entry.version)"

        # A prova central de hermetismo: a procedencia tem de estar sob o cache
        # do workspace. Uma copia global satisfaria "importa" e "versao".
        $origin = [string]$entry.origin
        $underCache = $origin.StartsWith((Resolve-Path -LiteralPath $cachePath).Path, [System.StringComparison]::OrdinalIgnoreCase)
        Assert-True "$importName vem do cache do workspace" $underCache "origin=$origin"
    }
}

# ---------------------------------------------------------------------------
# 4. Modo offline: cache ausente BLOQUEIA em vez de baixar
# ---------------------------------------------------------------------------

# Aponta o helper para um workspace sintetico com lock valido e cache vazio.
# Sem rede autorizada, isto tem de lancar; se retornasse "ready", os gates
# poderiam baixar dependencia no meio da execucao.
$fakeRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("py_herm_" + [guid]::NewGuid().ToString("N"))
try {
    $fakeWrapper = Join-Path (Join-Path $fakeRoot 'tools') 'sgdk_wrapper'
    New-Item -ItemType Directory -Force -Path $fakeWrapper | Out-Null
    Copy-Item -LiteralPath $lockPath -Destination (Join-Path $fakeWrapper 'linux_python_requirements.lock')

    $blocked = $false
    $reason = ''
    try {
        Invoke-PythonProvisioning -WorkspaceRoot $fakeRoot -AllowNetwork $false | Out-Null
    } catch {
        $reason = $_.Exception.Message
        $blocked = $reason -like '*python_provisioning_required*' -or $reason -like '*python_cache_missing*'
    }
    Assert-True "cache ausente bloqueia em modo offline" $blocked "motivo='$reason'"

    # E a mensagem precisa apontar o caminho de correcao, nao apenas falhar.
    Assert-True "blocker aponta o provisionador" ($reason -like '*ensure_linux_python_deps.sh*') "motivo='$reason'"
}
finally {
    Remove-Item -LiteralPath $fakeRoot -Recurse -Force -ErrorAction SilentlyContinue
}

# ---------------------------------------------------------------------------
# 5. Divergencia de versao e detectada
# ---------------------------------------------------------------------------

# Reescreve o lock sintetico com uma versao impossivel e confirma que o assert
# reprova. Sem isto, "versao do lock" seria uma afirmacao nao testada.
$driftRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("py_drift_" + [guid]::NewGuid().ToString("N"))
try {
    $driftWrapper = Join-Path (Join-Path $driftRoot 'tools') 'sgdk_wrapper'
    New-Item -ItemType Directory -Force -Path $driftWrapper | Out-Null

    # Mesmo lock, versao de jsonschema trocada por uma que nao existe no cache.
    $driftLock = ($lockText -replace 'jsonschema==[0-9.]+', 'jsonschema==0.0.1')
    Set-Content -LiteralPath (Join-Path $driftWrapper 'linux_python_requirements.lock') -Value $driftLock -Encoding UTF8

    # Reaproveita o cache REAL, para isolar a variavel: so a versao esperada mudou.
    $driftCache = Join-Path (Join-Path (Join-Path $driftRoot 'out') 'host_tools') 'python'
    New-Item -ItemType Directory -Force -Path $driftCache | Out-Null
    New-Item -ItemType SymbolicLink -Path (Join-Path $driftCache 'site-packages') -Target (Resolve-Path -LiteralPath $cachePath).Path | Out-Null

    $detected = $false
    $driftReason = ''
    try {
        Assert-PythonDependencies -WorkspaceRoot $driftRoot | Out-Null
    } catch {
        $driftReason = $_.Exception.Message
        $detected = $driftReason -like '*version_mismatch*'
    }
    Assert-True "divergencia de versao vs lock e detectada" $detected "motivo='$driftReason'"
}
finally {
    Remove-Item -LiteralPath $driftRoot -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
if ($failures.Count -gt 0) {
    Write-Host "python dependency hermeticity: $checks verificacoes, $($failures.Count) falha(s)"
    foreach ($failure in $failures) { Write-Host "- $failure" }
    exit 1
}

Write-Host "PASS python dependency hermeticity ($checks verificacoes, cache=$cachePath)"
exit 0
