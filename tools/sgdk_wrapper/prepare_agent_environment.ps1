<#
.SYNOPSIS
  Prepara o ambiente consultivo dos agentes SGDK Forge no inicio da sessao.

.DESCRIPTION
  Este script e seguro para primeiro uso:
  - garante as pontes .agents/skills e .trae/skills para a arvore canonica;
  - verifica pwsh, uv e graphify;
  - prepara a integracao consultiva ai-memory sem instalar hooks globais;
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
    [switch]$SkipGraphify,

    [Parameter(Mandatory = $false)]
    [switch]$SkipAiMemory,

    [Parameter(Mandatory = $false)]
    [ValidateRange(1, 3600)]
    [int]$GraphifyTimeoutSeconds = 60
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
    $homeRoot = $env:USERPROFILE
    if ([string]::IsNullOrWhiteSpace($homeRoot)) { $homeRoot = $env:HOME }
    if ([string]::IsNullOrWhiteSpace($homeRoot)) { $homeRoot = [Environment]::GetFolderPath('UserProfile') }
    if ([string]::IsNullOrWhiteSpace($homeRoot)) { $homeRoot = "" }
    $localBin = if ([string]::IsNullOrWhiteSpace($homeRoot)) { "" } else { Join-Path $homeRoot ".local/bin" }
    if (-not [string]::IsNullOrWhiteSpace($localBin) -and (Test-Path -LiteralPath $localBin)) { $parts += $localBin }
    if ($parts.Count -gt 0) { $env:Path = ($parts -join [System.IO.Path]::PathSeparator) }
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

function Resolve-PowerShellHost {
    $pwsh = Get-Command pwsh -ErrorAction SilentlyContinue
    if ($null -ne $pwsh) { return $pwsh.Source }

    $powershell = Get-Command powershell -ErrorAction SilentlyContinue
    if ($null -ne $powershell) { return $powershell.Source }

    $powershellExe = Get-Command powershell.exe -ErrorAction SilentlyContinue
    if ($null -ne $powershellExe) { return $powershellExe.Source }

    throw "Nenhum host PowerShell encontrado (pwsh/powershell/powershell.exe)."
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
$aiMemoryReady = $false
$aiMemoryStatus = "not_checked"
$aiMemoryCliPresent = $false
$aiMemoryReportPath = Join-Path $root "out\logs\ai_memory_integration_report.json"
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
if (-not $SkipGraphify) {
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
} else {
    $uvOk = Test-CommandAvailable -Name 'uv'
    $graphifyOk = Test-CommandAvailable -Name 'graphify'
    Write-AgentEnvLog "INFO" "Graphify e uv nao sao obrigatorios porque -SkipGraphify foi solicitado."
}

if (-not $SkipAiMemory) {
    $aiMemoryScript = Join-Path $root "tools\sgdk_wrapper\prepare_ai_memory_integration.ps1"
    if (-not (Test-Path -LiteralPath $aiMemoryScript -PathType Leaf)) {
        Write-AgentEnvLog "ERROR" "Wrapper ai-memory ausente: $aiMemoryScript"
        $aiMemoryStatus = "script_missing"
        $failures++
    } else {
        try {
            $powerShellHost = Resolve-PowerShellHost
            $aiOut = (& $powerShellHost -NoProfile -ExecutionPolicy Bypass -File $aiMemoryScript -RepoRoot $root -Mode Prepare -OutputFormat Json 2>&1 | Out-String)
            if ($LASTEXITCODE -ne 0) {
                Write-AgentEnvLog "ERROR" "Falha ao preparar ai-memory consultivo."
                Write-Host $aiOut.TrimEnd()
                $aiMemoryStatus = "prepare_failed"
                $failures++
            } else {
                $aiReport = $aiOut | ConvertFrom-Json
                $aiMemoryReady = [bool]$aiReport.ready
                $aiMemoryCliPresent = [bool]$aiReport.ai_memory_cli.present
                $aiMemoryStatus = if ($aiMemoryReady) { "prepared" } else { "not_ready" }
                Write-AgentEnvLog "OK" ("ai-memory consultivo preparado (cli_present={0})." -f $aiMemoryCliPresent.ToString().ToLowerInvariant())
                if (-not $aiMemoryReady) {
                    $failures++
                }
            }
        } catch {
            Write-AgentEnvLog "ERROR" "Excecao preparando ai-memory consultivo: $($_.Exception.Message)"
            $aiMemoryStatus = "exception"
            $failures++
        }
    }
} else {
    $aiMemoryStatus = "skipped"
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
    $statusOut = (& pwsh -NoProfile -ExecutionPolicy Bypass -File $graphifyWrapper -Action status -RepoRoot $root -GraphifyTimeoutSeconds $GraphifyTimeoutSeconds 2>&1 | Out-String)
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
        & pwsh -NoProfile -ExecutionPolicy Bypass -File $graphifyWrapper -Action $action -RepoRoot $root -GraphifyTimeoutSeconds $GraphifyTimeoutSeconds @extra | Out-Host
        if ($LASTEXITCODE -ne 0 -and $action -eq 'update') {
            Write-AgentEnvLog "WARN" "Update falhou; tentando build limpo."
            & pwsh -NoProfile -ExecutionPolicy Bypass -File $graphifyWrapper -Action build -RepoRoot $root -Force -GraphifyTimeoutSeconds $GraphifyTimeoutSeconds | Out-Host
        }

        $finalStatus = (& pwsh -NoProfile -ExecutionPolicy Bypass -File $graphifyWrapper -Action status -RepoRoot $root -GraphifyTimeoutSeconds $GraphifyTimeoutSeconds 2>&1 | Out-String)
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
    skip_ai_memory = [bool]$SkipAiMemory
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
        timeout_seconds = [int]$GraphifyTimeoutSeconds
    }
    ai_memory = [pscustomobject]@{
        status = $aiMemoryStatus
        ready = [bool]$aiMemoryReady
        cli_present = [bool]$aiMemoryCliPresent
        report = $aiMemoryReportPath
        wrapper = "tools/sgdk_wrapper/prepare_ai_memory_integration.ps1"
        policy = "consultive_optional_layer"
        closeout_gate = $false
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
