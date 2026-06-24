[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('production_visual', 'technical', 'lab')]
    [string]$AdmissionType,

    [string]$RouteReportPath,

    [string]$TechnicalChangeScopePath,

    [string]$LabReason,

    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'

$ModulePath = Join-Path $PSScriptRoot 'lib\runtime_admission.psm1'
Import-Module $ModulePath -Force

$Report = New-RuntimeAdmissionReport `
    -AdmissionType $AdmissionType `
    -RouteReportPath $RouteReportPath `
    -TechnicalChangeScopePath $TechnicalChangeScopePath `
    -LabReason $LabReason

if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputDirectory = Split-Path -Parent $OutputPath
    if (-not [string]::IsNullOrWhiteSpace($OutputDirectory)) {
        New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    }
    $Report | ConvertTo-Json -Depth 100 | Set-Content -Encoding UTF8 -Path $OutputPath
}

$Report | ConvertTo-Json -Depth 100
