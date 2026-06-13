[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$ProjectRoot = (Get-Location).Path,

    [ValidateSet('Audit', 'Capture')]
    [string]$Mode = 'Audit',

    [ValidateSet('Host', 'Json')]
    [string]$OutputFormat = 'Host'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$extractor = Join-Path $PSScriptRoot '.agent\scripts\extract_project_learning.py'
if (-not (Test-Path -LiteralPath $extractor -PathType Leaf)) {
    Write-Error "Project learning extractor not found: $extractor"
    exit 1
}

$resolvedRoot = try {
    (Resolve-Path -LiteralPath $ProjectRoot -ErrorAction Stop).Path
} catch {
    Write-Error "ProjectRoot inexistente: $ProjectRoot"
    exit 1
}

$modeValue = $Mode.ToLowerInvariant()
$formatValue = $OutputFormat.ToLowerInvariant()

& py $extractor `
    --project-root $resolvedRoot `
    --mode $modeValue `
    --output-format $formatValue

exit $LASTEXITCODE
