[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ManifestPath,

    [string]$OutputPath,

    [switch]$FailOnBlocked
)

$ErrorActionPreference = 'Stop'

$ModulePath = Join-Path $PSScriptRoot 'lib\premium_source_manifest.psm1'
Import-Module $ModulePath -Force

$Report = Test-PremiumSourceManifestFile -ManifestPath $ManifestPath

if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputDirectory = Split-Path -Parent $OutputPath
    if (-not [string]::IsNullOrWhiteSpace($OutputDirectory)) {
        New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    }
    $Report | ConvertTo-Json -Depth 100 | Set-Content -Encoding UTF8 -Path $OutputPath
}

$Report | ConvertTo-Json -Depth 100

if ($FailOnBlocked -and $Report.status -eq 'blocked') {
    exit 2
}
