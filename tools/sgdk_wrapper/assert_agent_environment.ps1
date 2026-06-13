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
    [switch]$SkipGraphify
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

& powershell @args
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

Write-Host "agent_environment_status=ready report=$reportPath"
exit 0
