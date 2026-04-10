[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string[]]$Roots,

    [Parameter(Mandatory = $false)]
    [string]$RootsCsv
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-FullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Resolve-Path -LiteralPath $Path).Path
}

try {
    $wrapperDir = $PSScriptRoot
    $workspaceRoot = Resolve-FullPath -Path (Join-Path $wrapperDir "..\..")
    $alignScript = Join-Path $wrapperDir "validate_and_align_worktree.ps1"
    if (-not (Test-Path -LiteralPath $alignScript -PathType Leaf)) {
        throw "Missing align script: '$alignScript'."
    }

    $effectiveRoots = @()
    if ($Roots -and $Roots.Count -gt 0) { $effectiveRoots += $Roots }
    if (-not [string]::IsNullOrWhiteSpace($RootsCsv)) {
        $effectiveRoots += @($RootsCsv -split ';' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    }
    if (-not $effectiveRoots -or $effectiveRoots.Count -eq 0) {
        throw "Nenhuma raiz fornecida. Use -Roots ou -RootsCsv."
    }

    $projects = New-Object System.Collections.Generic.List[string]
    foreach ($root in $effectiveRoots) {
        $r = Resolve-FullPath -Path $root
        if (-not (Test-Path -LiteralPath $r -PathType Container)) { continue }

        $bats = Get-ChildItem -LiteralPath $r -Recurse -Force -File -Filter "build.bat" -ErrorAction SilentlyContinue
        foreach ($b in $bats) {
            $projects.Add($b.Directory.FullName) | Out-Null
        }
    }

    $unique = $projects | Sort-Object -Unique
    $total = $unique.Count
    $ok = 0
    $fail = 0

    foreach ($proj in $unique) {
        Write-Host ("[ALIGN] {0}" -f $proj)
        & powershell -NoProfile -ExecutionPolicy Bypass -File $alignScript -ProjectRoot $proj -WorkspaceRoot $workspaceRoot -Fix
        if ($LASTEXITCODE -eq 0) { $ok++ } else { $fail++ }
    }

    Write-Host ("[SUMMARY] total={0} ok={1} fail={2}" -f $total, $ok, $fail)
    if ($fail -gt 0) { exit 1 }
    exit 0
}
catch {
    Write-Error $_
    exit 1
}

