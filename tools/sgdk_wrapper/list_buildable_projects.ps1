[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string[]]$Roots,

    [int]$Limit = 10
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Try-ReadJson {
    param([Parameter(Mandatory = $true)][string]$Path)
    try {
        return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json)
    } catch {
        return $null
    }
}

try {
    $results = New-Object System.Collections.Generic.List[object]

    foreach ($root in $Roots) {
        if (-not (Test-Path -LiteralPath $root -PathType Container)) { continue }
        Get-ChildItem -LiteralPath $root -Recurse -Force -File -Filter "project.json" -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -like "*\.mddev\project.json" } |
            ForEach-Object {
                $json = Try-ReadJson -Path $_.FullName
                if ($null -eq $json) { return }

                $bp = $null
                if ($json.PSObject.Properties["build_policy"]) { $bp = [string]$json.build_policy }
                elseif ($json.PSObject.Properties["buildPolicy"]) { $bp = [string]$json.buildPolicy }
                if ([string]::IsNullOrWhiteSpace($bp)) { $bp = "enabled" }

                if ($bp -eq "disabled") { return }

                $proj = Split-Path -Parent (Split-Path -Parent $_.FullName)
                if (-not (Test-Path -LiteralPath (Join-Path $proj "src"))) { return }

                $results.Add([pscustomobject]@{
                    Project = $proj
                    BuildPolicy = $bp
                    Manifest = $_.FullName
                    HasInc = Test-Path -LiteralPath (Join-Path $proj "inc")
                    HasRes = Test-Path -LiteralPath (Join-Path $proj "res")
                }) | Out-Null
            }
    }

    $results | Sort-Object Project | Select-Object -First $Limit | Format-Table -AutoSize
    exit 0
}
catch {
    Write-Error $_
    exit 1
}

