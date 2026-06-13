[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ProjectDir = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectDir)) {
    $ProjectDir = (Get-Location).Path
}

$ProjectDir = (Resolve-Path -LiteralPath $ProjectDir).Path
$validateScript = Join-Path $PSScriptRoot "validate_resources.ps1"

if (-not (Test-Path -LiteralPath $validateScript)) {
    throw "validate_resources.ps1 nao encontrado em $validateScript"
}

& $validateScript -WorkDir $ProjectDir
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao revalidar o projeto com metricas de runtime."
}
