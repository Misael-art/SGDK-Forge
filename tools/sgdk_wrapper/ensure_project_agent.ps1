[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SourceDir,

    [Parameter(Mandatory = $true)]
    [string]$TargetDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-FullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

try {
    $resolvedSource = Resolve-FullPath -Path $SourceDir
    $resolvedTarget = Resolve-FullPath -Path $TargetDir

    if (-not (Test-Path -LiteralPath $resolvedSource -PathType Container)) {
        throw "Diretorio fonte da .agent nao encontrado: '$resolvedSource'."
    }

    $sourceArchitecture = Join-Path $resolvedSource "ARCHITECTURE.md"
    if (-not (Test-Path -LiteralPath $sourceArchitecture -PathType Leaf)) {
        throw "A .agent canonica esta incompleta. Arquivo obrigatorio ausente: '$sourceArchitecture'."
    }

    if (-not (Test-Path -LiteralPath $resolvedTarget -PathType Container)) {
        throw "Diretorio do projeto nao encontrado: '$resolvedTarget'."
    }

    $destinationAgentDir = Join-Path $resolvedTarget ".agent"
    if (Test-Path -LiteralPath $destinationAgentDir -PathType Container) {
        Write-Host "[SGDK Wrapper] .agent local ja existe em: $destinationAgentDir"
        exit 0
    }

    New-Item -ItemType Directory -Path $destinationAgentDir -Force | Out-Null

    foreach ($child in Get-ChildItem -LiteralPath $resolvedSource -Force) {
        Copy-Item -LiteralPath $child.FullName -Destination $destinationAgentDir -Recurse -Force
    }

    $copiedArchitecture = Join-Path $destinationAgentDir "ARCHITECTURE.md"
    if (-not (Test-Path -LiteralPath $copiedArchitecture -PathType Leaf)) {
        throw "Falha ao copiar a .agent canonica para '$resolvedTarget'. O arquivo '$copiedArchitecture' nao foi materializado."
    }

    Write-Host "[SGDK Wrapper] .agent bootstrap copiada para: $resolvedTarget"
    exit 0
}
catch {
    Write-Error $_
    exit 1
}
