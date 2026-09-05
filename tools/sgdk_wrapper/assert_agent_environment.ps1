<#
.SYNOPSIS
  Guarda automatica para agentes SGDK Forge.

.DESCRIPTION
  Executa o preparo comum quando necessario e valida que o ambiente ficou pronto.
  Este e o comando preferencial para agentes: ele reduz dependencia humana porque
  chama `prepare_agent_environment.ps1` por conta propria.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$RepoRoot = "",

    [Parameter(Mandatory = $false)]
    [switch]$NoInstallMissing,

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

function Resolve-PowerShellHost {
    $pwsh = Get-Command pwsh -ErrorAction SilentlyContinue
    if ($null -ne $pwsh) { return $pwsh.Source }

    $powershell = Get-Command powershell -ErrorAction SilentlyContinue
    if ($null -ne $powershell) { return $powershell.Source }

    $powershellExe = Get-Command powershell.exe -ErrorAction SilentlyContinue
    if ($null -ne $powershellExe) { return $powershellExe.Source }

    throw "Nenhum host PowerShell encontrado (pwsh/powershell/powershell.exe)."
}

$root = Resolve-ForgedRepoRoot -ExplicitRoot $RepoRoot
$prepare = Join-Path $root "tools\sgdk_wrapper\prepare_agent_environment.ps1"
$reportPath = Join-Path $root "graphify-out\AGENT_ENVIRONMENT_REPORT.json"

$args = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", $prepare,
    "-RepoRoot", $root
)
if (-not $NoInstallMissing) { $args += "-InstallMissing" }
if ($SkipGraphify) { $args += "-SkipGraphify" }
if ($SkipAiMemory) { $args += "-SkipAiMemory" }
$args += @("-GraphifyTimeoutSeconds", $GraphifyTimeoutSeconds)

$powerShellHost = Resolve-PowerShellHost
& $powerShellHost @args
if ($LASTEXITCODE -ne 0) {
    Write-Host "agent_environment_status=blocked reason=prepare_failed"
    exit 1
}

if (-not (Test-Path -LiteralPath $reportPath -PathType Leaf)) {
    Write-Host "agent_environment_status=blocked reason=report_missing"
    exit 1
}

$report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
if (-not [bool]$report.ready) {
    Write-Host "agent_environment_status=blocked reason=report_not_ready"
    exit 1
}

if (-not $SkipGraphify) {
    $graphStatus = [string]$report.graphify.status
    if ($graphStatus -ne "fresh") {
        Write-Host "agent_environment_status=blocked reason=graph_not_fresh graph_status=$graphStatus"
        exit 1
    }
}

# Persistence / host-operation route. Non-fatal: exposes the session's
# persistence policy (GUI policy, write confinement, forbidden routes) so the
# agent never falls back to a GUI picker or ~/Downloads for deterministic work.
# A failure here is a warning, never a blocker of the environment.
try {
    $router = Join-Path $PSScriptRoot "host_operation_router.py"
    $pyHost = Resolve-PowerShellHost
    if ($null -ne $pyHost -and (Test-Path -LiteralPath $router -PathType Leaf)) {
        $persistDir = Join-Path $root "out\logs"
        if (-not (Test-Path -LiteralPath $persistDir -PathType Container)) {
            New-Item -ItemType Directory -Force -Path $persistDir | Out-Null
        }
        $persistReport = Join-Path $persistDir "persistence_route_report.json"
        $op = "persist_editor_export"
        $projectArg = ""
        $activeProjectProp = $report.PSObject.Properties['active_project']
        if ($null -ne $activeProjectProp -and $activeProjectProp.Value) {
            $projectResolved = Join-Path $root $activeProjectProp.Value
            if (Test-Path -LiteralPath $projectResolved -PathType Container) {
                $projectArg = "--project-root `"$projectResolved`""
            }
        }
        & $pyHost -NoProfile -ExecutionPolicy Bypass -Command "python3 '$router' --operation '$op' $projectArg --repo-root '$root' --output '$persistReport' 2>&1" | Out-Null
        Set-Item -Path "env:SGDK_PERSISTENCE_ROUTE" -Value $persistReport -ErrorAction SilentlyContinue
        Write-Host "persistence_route=$persistReport operation=$op"
    }
} catch {
    Write-Host "persistence_route=warn reason=$($_.Exception.Message)"
}

Write-Host "agent_environment_status=ready report=$reportPath"
exit 0
