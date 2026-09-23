[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RequestText,

    [string]$ProjectRoot = (Get-Location).Path,

    [string]$OutputPath,

    [string]$CompactOutputPath,

    [switch]$SkipGraphify
)

$ErrorActionPreference = 'Stop'

$ModulePath = Join-Path $PSScriptRoot 'lib\vibe_playable_router.psm1'
Import-Module $ModulePath -Force

$Report = New-VibePlayableRouteReport `
    -RequestText $RequestText `
    -ProjectRoot $ProjectRoot `
    -SkipGraphify:$SkipGraphify

if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputDirectory = Split-Path -Parent $OutputPath
    if (-not [string]::IsNullOrWhiteSpace($OutputDirectory)) {
        New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    }
    $Report | ConvertTo-Json -Depth 100 | Set-Content -Encoding UTF8 -Path $OutputPath
}

if (-not [string]::IsNullOrWhiteSpace($CompactOutputPath)) {
    $CompactDirectory = Split-Path -Parent $CompactOutputPath
    if (-not [string]::IsNullOrWhiteSpace($CompactDirectory)) {
        New-Item -ItemType Directory -Force -Path $CompactDirectory | Out-Null
    }
    $Report.compact_context | ConvertTo-Json -Depth 100 | Set-Content -Encoding UTF8 -Path $CompactOutputPath
}

$Report | ConvertTo-Json -Depth 100
