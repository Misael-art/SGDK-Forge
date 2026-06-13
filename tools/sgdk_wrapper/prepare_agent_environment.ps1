<#
.SYNOPSIS
  Prepara o ambiente consultivo dos agentes SGDK Forge no inicio da sessao.

.DESCRIPTION
  Este script e seguro para primeiro uso:
  - garante as pontes .agents/skills e .trae/skills para a arvore canonica;
  - verifica pwsh, uv e graphify;
  - com -InstallMissing, tenta instalar dependencias ausentes via winget/uv;
  - prepara o grafo consultivo via graphify_forge.ps1 e deixa graph_status=fresh.

  Graphify continua sendo apenas indice consultivo. A decisao canonica sempre exige
  abrir os arquivos citados pelo grafo.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$RepoRoot = "",

    [Parameter(Mandatory = $false)]
    [switch]$InstallMissing,

    [Parameter(Mandatory = $false)]
    [switch]$SkipGraphify
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-AgentEnvLog {
    param([string]$Level, [string]$Message)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host ("[{0}] [{1}] {2}" -f $ts, $Level, $Message)
}

function Test-CommandAvailable {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Refresh-ProcessPath {
    $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $parts = @()
    if (-not [string]::IsNullOrWhiteSpace($machinePath)) { $parts += $machinePath }
    if (-not [string]::IsNullOrWhiteSpace($userPath)) { $parts += $userPath }
    $localBin = Join-Path $env:USERPROFILE ".local\bin"
    if (Test-Path -LiteralPath $localBin) { $parts += $localBin }
    if ($parts.Count -gt 0) { $env:Path = ($parts -join ';') }
}

function Resolve-ForgedRepoRoot {
    param([string]$ExplicitRoot)
    if (-not [string]::IsNullOrWhiteSpace($ExplicitRoot)) {
        return (Resolve-Path -LiteralPath $ExplicitRoot).Path
    }
    $wrapperDirInfo = [System.IO.DirectoryInfo]$PSScriptRoot
    $toolsDirInfo = $wrapperDirInfo.Parent
    $rootDirInfo = $toolsDirInfo.Parent
    return [System.IO.Path]::GetFullPath($rootDirInfo.FullName)
}

function Invoke-WingetInstall {
    param(
        [Parameter(Mandatory = $true)][string]$Id,
        [Parameter(Mandatory = $true)][string]$Label
    )

    if (-not (Test-CommandAvailable -Name 'winget')) {
        Write-AgentEnvLog "WARN" "winget indisponivel; nao foi possivel instalar $Label automaticamente."
        return $false
    }

    $args = @(
        'install',
        '--id', $Id,
        '-e',
        '--accept-package-agreements',
        '--accept-source-agreements',
        '--silent'
    )

    Write-AgentEnvLog "INFO" "Instalando $Label via winget."
    $process = Start-Process winget -ArgumentList $args -Wait -NoNewWindow -PassThru
    Refresh-ProcessPath
    return ($process.ExitCode -eq 0 -or $process.ExitCode -eq -1978335189)
}

function Ensure-Command {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $false)][string]$WingetId = ""
    )

    Refresh-ProcessPath
    if (Test-CommandAvailable -Name $Name) {
        Write-AgentEnvLog "OK" "$Label encontrado."
        return $true
    }

    if (-not $InstallMissing) {
        Write-AgentEnvLog "ERROR" "$Label ausente. Reexecute com -InstallMissing ou instale manualmente."
        return $false
    }

    if ([string]::IsNullOrWhiteSpace($WingetId)) {
        Write-AgentEnvLog "ERROR" "$Label ausente e sem instalador automatico registrado."
        return $false
    }

    if (-not (Invoke-WingetInstall -Id $WingetId -Label $Label)) {
        Write-AgentEnvLog "ERROR" "Falha ao instalar $Label."
        return $false
    }

    Refresh-ProcessPath
    if (Test-CommandAvailable -Name $Name) {
        Write-AgentEnvLog "OK" "$Label instalado."
        return $true
    }

    Write-AgentEnvLog "ERROR" "$Label ainda nao apareceu no PATH apos instalacao."
    return $false
}

function Ensure-RelativeBridge {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRootPath,
        [Parameter(Mandatory = $true)][string]$BridgePath,
        [Parameter(Mandatory = $true)][string]$TargetRelative
    )

    $fullBridge = Join-Path $RepoRootPath $BridgePath
    $parent = Split-Path $fullBridge -Parent
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }

    $targetFull = Join-Path $RepoRootPath ($TargetRelative.Replace('..\', ''))
    if (Test-Path -LiteralPath $fullBridge) {
        try {
            $item = Get-Item -LiteralPath $fullBridge -Force
            if ($item.LinkType -and (Test-Path -LiteralPath $fullBridge)) {
                Write-AgentEnvLog "OK" "$BridgePath presente."
                return $true
            }
            if ($item.PSIsContainer -and (Test-Path -LiteralPath (Join-Path $fullBridge 'art'))) {
                Write-AgentEnvLog "WARN" "$BridgePath existe como diretorio real; nao sobrescrevendo."
                return $true
            }
        } catch {
            Write-AgentEnvLog "WARN" "Nao foi possivel inspecionar ${BridgePath}: $($_.Exception.Message)"
        }
    }

    if (Test-Path -LiteralPath $fullBridge) {
        Write-AgentEnvLog "WARN" "$BridgePath existe mas nao e ponte reconhecida; mantendo sem sobrescrever."
        return $true
    }

    try {
        New-Item -ItemType SymbolicLink -Path $fullBridge -Target $TargetRelative | Out-Null
        Write-AgentEnvLog "OK" "$BridgePath criado como symlink relativo."
        return $true
    } catch {
        Write-AgentEnvLog "WARN" "Symlink falhou para $BridgePath; tentando junction. Detalhe: $($_.Exception.Message)"
        if (Test-Path -LiteralPath $targetFull) {
            New-Item -ItemType Junction -Path $fullBridge -Target $targetFull | Out-Null
            Write-AgentEnvLog "OK" "$BridgePath criado como junction fallback."
            return $true
        }
    }

    Write-AgentEnvLog "ERROR" "Nao foi possivel criar $BridgePath."
    return $false
}

$root = Resolve-ForgedRepoRoot -ExplicitRoot $RepoRoot
$failures = 0
$bridgeAgentsOk = $false
$bridgeTraeOk = $false
$pwshOk = $false
$uvOk = $false
$graphifyOk = $false
$graphStatus = "not_checked"
$graphReason = ""
$reportPath = Join-Path $root "graphify-out\AGENT_ENVIRONMENT_REPORT.json"
$agentEnvMutex = $null
$agentEnvLockTaken = $false

Write-AgentEnvLog "INFO" "Preparando ambiente de agente em $root"

$bridgeAgentsOk = Ensure-RelativeBridge -RepoRootPath $root -BridgePath ".agents\skills" -TargetRelative "..\tools\sgdk_wrapper\.agent\skills"
if (-not $bridgeAgentsOk) { $failures++ }
$bridgeTraeOk = Ensure-RelativeBridge -RepoRootPath $root -BridgePath ".trae\skills" -TargetRelative "..\tools\sgdk_wrapper\.agent\skills"
if (-not $bridgeTraeOk) { $failures++ }

$pwshOk = Ensure-Command -Name 'pwsh' -Label 'PowerShell 7 (pwsh)' -WingetId 'Microsoft.PowerShell'
if (-not $pwshOk) { $failures++ }
$uvOk = Ensure-Command -Name 'uv' -Label 'uv' -WingetId 'astral-sh.uv'
if (-not $uvOk) { $failures++ }

Refresh-ProcessPath
if (-not (Test-CommandAvailable -Name 'graphify')) {
    if ($InstallMissing -and (Test-CommandAvailable -Name 'uv')) {
        Write-AgentEnvLog "INFO" "Instalando Graphify via uv tool install graphifyy."
        & uv tool install graphifyy | Out-Host
        Refresh-ProcessPath
    }
}

if (Test-CommandAvailable -Name 'graphify') {
    Write-AgentEnvLog "OK" "Graphify encontrado."
    $graphifyOk = $true
} else {
    Write-AgentEnvLog "ERROR" "Graphify ausente. Instale com: uv tool install graphifyy"
    $failures++
}

if (-not $SkipGraphify -and $failures -eq 0) {
    $agentEnvMutex = New-Object System.Threading.Mutex($false, "Global\SGDKForgeAgentEnvironment")
    try {
        $agentEnvLockTaken = $agentEnvMutex.WaitOne([TimeSpan]::FromMinutes(10))
        if (-not $agentEnvLockTaken) {
            Write-AgentEnvLog "ERROR" "Timeout aguardando lock global SGDKForgeAgentEnvironment."
            $failures++
        }
    } catch {
        Write-AgentEnvLog "ERROR" "Falha ao adquirir lock global SGDKForgeAgentEnvironment: $($_.Exception.Message)"
        $failures++
    }
}

if (-not $SkipGraphify -and $failures -gt 0 -and $null -ne $agentEnvMutex) {
    if ($agentEnvLockTaken) {
        $agentEnvMutex.ReleaseMutex()
        $agentEnvLockTaken = $false
    }
    $agentEnvMutex.Dispose()
    $agentEnvMutex = $null
}

if (-not $SkipGraphify -and $failures -eq 0) {
    try {
    $graphifyWrapper = Join-Path $root "tools\sgdk_wrapper\graphify_forge.ps1"
    $statusOut = (& pwsh -NoProfile -ExecutionPolicy Bypass -File $graphifyWrapper -Action status -RepoRoot $root 2>&1 | Out-String)
    Write-Host $statusOut.TrimEnd()
    if ($statusOut -match 'graph_status=([a-z_]+)\s+reason=([a-z_]+)') {
        $graphStatus = $Matches[1]
        $graphReason = $Matches[2]
    }

    if ($statusOut -notmatch 'graph_status=fresh') {
        $action = 'update'
        $extra = @()
        if ($statusOut -match 'graph_missing|freshness_missing|graph_scope_violation') {
            $action = 'build'
            $extra += '-Force'
        }

        Write-AgentEnvLog "INFO" "Preparando Graphify com action=$action."
        & pwsh -NoProfile -ExecutionPolicy Bypass -File $graphifyWrapper -Action $action -RepoRoot $root @extra | Out-Host
        if ($LASTEXITCODE -ne 0 -and $action -eq 'update') {
            Write-AgentEnvLog "WARN" "Update falhou; tentando build limpo."
            & pwsh -NoProfile -ExecutionPolicy Bypass -File $graphifyWrapper -Action build -RepoRoot $root -Force | Out-Host
        }

        $finalStatus = (& pwsh -NoProfile -ExecutionPolicy Bypass -File $graphifyWrapper -Action status -RepoRoot $root 2>&1 | Out-String)
        Write-Host $finalStatus.TrimEnd()
        if ($finalStatus -match 'graph_status=([a-z_]+)\s+reason=([a-z_]+)') {
            $graphStatus = $Matches[1]
            $graphReason = $Matches[2]
        }
        if ($finalStatus -notmatch 'graph_status=fresh') {
            Write-AgentEnvLog "ERROR" "Graphify nao ficou fresh apos preparacao."
            $failures++
        }
    }
    } finally {
        if ($agentEnvLockTaken) {
            $agentEnvMutex.ReleaseMutex()
        }
        if ($null -ne $agentEnvMutex) {
            $agentEnvMutex.Dispose()
        }
    }
} elseif ($SkipGraphify) {
    $graphStatus = "skipped"
    $graphReason = "skip_graphify"
}

$reportDir = Split-Path -Parent $reportPath
if (-not (Test-Path -LiteralPath $reportDir)) {
    New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
}

$report = [pscustomobject]@{
    schema_version = "1.0.0"
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    repo_root = $root
    ready = ($failures -eq 0)
    failures = [int]$failures
    install_missing_requested = [bool]$InstallMissing
    skip_graphify = [bool]$SkipGraphify
    checks = [pscustomobject]@{
        agents_skills_bridge = [bool]$bridgeAgentsOk
        trae_skills_bridge = [bool]$bridgeTraeOk
        pwsh = [bool]$pwshOk
        uv = [bool]$uvOk
        graphify = [bool]$graphifyOk
    }
    graphify = [pscustomobject]@{
        status = $graphStatus
        reason = $graphReason
        wrapper = "tools/sgdk_wrapper/graphify_forge.ps1"
        policy = "consultive_index_only"
    }
}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8
Write-AgentEnvLog "INFO" "Report=$reportPath"

if ($failures -gt 0) {
    Write-AgentEnvLog "ERROR" "Preparacao concluida com $failures falha(s)."
    exit 1
}

Write-AgentEnvLog "OK" "Ambiente de agente pronto."
exit 0
