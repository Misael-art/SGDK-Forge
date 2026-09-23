[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$BaselineDir,

    [Parameter(Mandatory = $true)]
    [string]$CurrentDir,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"

function Get-FirstDiffOffset {
    param(
        [byte[]]$Left,
        [byte[]]$Right
    )

    $minLength = [Math]::Min($Left.Length, $Right.Length)
    for ($i = 0; $i -lt $minLength; $i++) {
        if ($Left[$i] -ne $Right[$i]) {
            return $i
        }
    }

    if ($Left.Length -ne $Right.Length) {
        return $minLength
    }

    return $null
}

$baselineRoot = (Resolve-Path -LiteralPath $BaselineDir).Path
$currentRoot = (Resolve-Path -LiteralPath $CurrentDir).Path
$outputParent = Split-Path -Parent $OutputPath
if (-not [string]::IsNullOrWhiteSpace($outputParent)) {
    New-Item -ItemType Directory -Force -Path $outputParent | Out-Null
}

$files = @(
    "benchmark_visual.png",
    "save.sram",
    "visual_vdp_dump.bin"
)

$results = @()
foreach ($fileName in $files) {
    $baselinePath = Join-Path $baselineRoot $fileName
    $currentPath = Join-Path $currentRoot $fileName
    $baselineBytes = [System.IO.File]::ReadAllBytes($baselinePath)
    $currentBytes = [System.IO.File]::ReadAllBytes($currentPath)
    $firstDiffOffset = Get-FirstDiffOffset -Left $baselineBytes -Right $currentBytes

    $results += [ordered]@{
        file = $fileName
        identical = ($null -eq $firstDiffOffset)
        first_diff_offset = $firstDiffOffset
        baseline_bytes = $baselineBytes.Length
        current_bytes = $currentBytes.Length
        baseline_sha256 = (Get-FileHash -LiteralPath $baselinePath -Algorithm SHA256).Hash.ToLowerInvariant()
        current_sha256 = (Get-FileHash -LiteralPath $currentPath -Algorithm SHA256).Hash.ToLowerInvariant()
        baseline_path = $baselinePath
        current_path = $currentPath
    }
}

$payload = [ordered]@{
    generated_at = (Get-Date -Format "o")
    baseline_dir = $baselineRoot
    current_dir = $currentRoot
    files = $results
}

$payload | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $OutputPath
Get-Content -LiteralPath $OutputPath
