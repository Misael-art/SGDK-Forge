[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$WorkDir,

    [Parameter(Mandatory = $true)]
    [string]$RomPath,

    [ValidateSet("Batch", "Json")]
    [string]$OutputFormat = "Batch"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Convert-ToBatchLine {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Value
    )

    $safe = $Value.Replace('"', '""')
    return ('set "{0}={1}"' -f $Name, $safe)
}

function Get-NewestInput {
    param([Parameter(Mandatory = $true)][string]$BaseDir)

    $candidates = @()
    foreach ($name in @("src", "res", "inc")) {
        $path = Join-Path $BaseDir $name
        if (-not (Test-Path -LiteralPath $path -PathType Container)) {
            continue
        }

        $candidates += Get-ChildItem -LiteralPath $path -File -Recurse -ErrorAction SilentlyContinue
    }

    if (-not $candidates -or $candidates.Count -eq 0) {
        return $null
    }

    return $candidates | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
}

try {
    $workDirFull = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $WorkDir).Path)
    $romFull = [System.IO.Path]::GetFullPath($RomPath)
    $romExists = Test-Path -LiteralPath $romFull -PathType Leaf
    $newestInput = Get-NewestInput -BaseDir $workDirFull

    $result = [ordered]@{
        SGDK_ROM_EXISTS       = if ($romExists) { "1" } else { "0" }
        SGDK_ROM_NEEDS_BUILD  = "0"
        SGDK_ROM_REASON       = "current"
        SGDK_ROM_NEWEST_INPUT = ""
    }

    if ($newestInput) {
        $result["SGDK_ROM_NEWEST_INPUT"] = $newestInput.FullName
    }

    if (-not $romExists) {
        $result["SGDK_ROM_NEEDS_BUILD"] = "1"
        $result["SGDK_ROM_REASON"] = "missing"
    } elseif ($newestInput -and $newestInput.LastWriteTimeUtc -gt (Get-Item -LiteralPath $romFull).LastWriteTimeUtc) {
        $result["SGDK_ROM_NEEDS_BUILD"] = "1"
        $result["SGDK_ROM_REASON"] = "stale"
    }

    if ($OutputFormat -eq "Json") {
        [PSCustomObject]$result | ConvertTo-Json -Depth 3
        exit 0
    }

    foreach ($pair in $result.GetEnumerator()) {
        Convert-ToBatchLine -Name $pair.Key -Value ([string]$pair.Value)
    }
}
catch {
    Write-Error $_
    exit 1
}
