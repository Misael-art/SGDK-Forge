<#
.SYNOPSIS
    Validates the canonical SGDK project directory naming convention.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Name
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$canonicalPattern = '^[^\\/:*?"<>|\[\]\r\n]+ \[VER\.[0-9]+(?:\.[0-9]+)*\] \[SGDK [0-9]+\] \[[A-Z0-9][A-Z0-9 _-]*\] \[[A-Z0-9][A-Z0-9 _-]*\] \[[A-Z0-9][A-Z0-9 _-]*\]$'
$hasUnsafeSegment = $Name.Contains('..') -or $Name.Contains('\') -or $Name.Contains('/')

if ($hasUnsafeSegment -or $Name -notmatch $canonicalPattern) {
    Write-Host '[validate_project_name] invalid'
    Write-Host 'Expected: NOME [VER.XXX] [SGDK YYY] [PLATAFORMA] [TIPO] [GENERO]'
    exit 1
}

Write-Host '[validate_project_name] valid'
exit 0
